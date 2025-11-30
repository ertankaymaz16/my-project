"""
Appointment polling and reservation module
"""
import asyncio
import random
from typing import Optional, Dict
from playwright.async_api import Page
from utils.logger import logger
from utils.stealth import StealthHelper


class AppointmentManager:
    """Manages appointment searching and booking"""
    
    # VFS URLs (Update with actual URLs)
    APPOINTMENT_URL = "https://visa.vfsglobal.com/tur/tr/nld/book-an-appointment"
    
    def __init__(self, page: Page, criteria: dict, applicants: list):
        self.page = page
        self.criteria = criteria
        self.applicants = applicants
        self.stealth = StealthHelper()
        
        self.location = criteria.get('location', 'Bursa')
        self.visa_type = criteria.get('visa_type', 'Tourist')
        self.num_people = criteria.get('number_of_people', 2)
    
    async def start_polling(self, interval_minutes: int = 10, random_delay_range: tuple = (8, 12)) -> Optional[Dict]:
        """
        Start polling for appointments
        
        Args:
            interval_minutes: Base interval between checks
            random_delay_range: Random delay range in minutes when no appointment found
        
        Returns:
            Appointment details if found
        """
        attempt = 0
        
        while True:
            attempt += 1
            logger.phase("FAZ 2", f"Polling attempt #{attempt}")
            
            try:
                # Navigate to appointment page
                await self.page.goto(self.APPOINTMENT_URL, wait_until='networkidle', timeout=30000)
                await self.stealth.random_delay(1, 2)
                
                # Apply filters
                await self._apply_filters()
                
                # Check for available slots
                appointment = await self._check_availability()
                
                if appointment:
                    logger.success(f"🎯 APPOINTMENT FOUND! {appointment}")
                    return appointment
                else:
                    logger.info("No appointments available")
                    
                    # Random delay to avoid detection
                    delay_minutes = random.uniform(*random_delay_range)
                    logger.info(f"Waiting {delay_minutes:.1f} minutes before next check...")
                    await asyncio.sleep(delay_minutes * 60)
                    
            except Exception as e:
                logger.error(f"Error during polling: {str(e)}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _apply_filters(self):
        """Apply search filters (location, visa type, number of people)"""
        try:
            logger.info(f"Applying filters: {self.location}, {self.visa_type}, {self.num_people} people")
            
            # Select location (Bursa)
            location_selectors = [
                'select[name="location"]',
                'select#location',
                '#mat-select-location',
                'mat-select[formcontrolname="location"]'
            ]
            
            for selector in location_selectors:
                try:
                    element = await self.stealth.wait_for_element_safely(self.page, selector, timeout=5000)
                    if element:
                        await element.click()
                        await self.stealth.random_delay(0.3, 0.6)
                        
                        # Select Bursa option
                        option_selector = f'mat-option:has-text("{self.location}"), option:has-text("{self.location}")'
                        await self.page.click(option_selector, timeout=5000)
                        await self.stealth.random_delay(0.5, 1)
                        break
                except:
                    continue
            
            # Select visa type (Tourist)
            visa_type_selectors = [
                'select[name="visa_type"]',
                'select#visaType',
                '#mat-select-visa-type',
                'mat-select[formcontrolname="visaType"]'
            ]
            
            for selector in visa_type_selectors:
                try:
                    element = await self.stealth.wait_for_element_safely(self.page, selector, timeout=5000)
                    if element:
                        await element.click()
                        await self.stealth.random_delay(0.3, 0.6)
                        
                        # Select Tourist option
                        option_selector = f'mat-option:has-text("{self.visa_type}"), option:has-text("{self.visa_type}")'
                        await self.page.click(option_selector, timeout=5000)
                        await self.stealth.random_delay(0.5, 1)
                        break
                except:
                    continue
            
            # Select number of people
            num_people_selectors = [
                'select[name="applicants"]',
                'select#numberOfApplicants',
                'input[name="applicants"]',
                '#mat-select-applicants'
            ]
            
            for selector in num_people_selectors:
                try:
                    element = await self.stealth.wait_for_element_safely(self.page, selector, timeout=5000)
                    if element:
                        tag_name = await element.evaluate('el => el.tagName')
                        
                        if tag_name.lower() == 'input':
                            await element.fill(str(self.num_people))
                        else:
                            await element.click()
                            await self.stealth.random_delay(0.3, 0.6)
                            option_selector = f'mat-option:has-text("{self.num_people}"), option[value="{self.num_people}"]'
                            await self.page.click(option_selector, timeout=5000)
                        
                        await self.stealth.random_delay(0.5, 1)
                        break
                except:
                    continue
            
            # Click search/check availability button
            search_button_selectors = [
                'button:has-text("Search")',
                'button:has-text("Check Availability")',
                'button:has-text("Ara")',
                'button:has-text("Müsaitlik Kontrol")',
                'button[type="submit"]',
                '.btn-search',
                '#btnSearch'
            ]
            
            for selector in search_button_selectors:
                try:
                    await self.page.click(selector, timeout=5000)
                    await self.stealth.random_delay(1, 2)
                    break
                except:
                    continue
            
            logger.debug("Filters applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying filters: {str(e)}", exc_info=True)
    
    async def _check_availability(self) -> Optional[Dict]:
        """Check if appointments are available"""
        try:
            await asyncio.sleep(2)  # Wait for results to load
            
            # Look for available slots
            slot_selectors = [
                '.appointment-slot.available',
                '.slot.available',
                'button.appointment-available',
                '.calendar-day.available',
                '[data-available="true"]',
                '.available-slot'
            ]
            
            for selector in slot_selectors:
                try:
                    slots = await self.page.query_selector_all(selector)
                    if slots and len(slots) > 0:
                        # Get first available slot details
                        first_slot = slots[0]
                        
                        # Extract date and time
                        date_text = await first_slot.get_attribute('data-date') or await first_slot.inner_text()
                        time_text = await first_slot.get_attribute('data-time') or ""
                        
                        appointment = {
                            'location': self.location,
                            'visa_type': self.visa_type,
                            'people': self.num_people,
                            'date': date_text,
                            'time': time_text,
                            'element': first_slot
                        }
                        
                        return appointment
                except:
                    continue
            
            # Check for "no appointments" message
            no_slots_indicators = [
                'text=No appointments available',
                'text=Müsait randevu yok',
                'text=No slots',
                '.no-appointments',
                '.no-availability'
            ]
            
            for indicator in no_slots_indicators:
                try:
                    element = await self.page.wait_for_selector(indicator, timeout=2000, state='visible')
                    if element:
                        return None
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}", exc_info=True)
            return None
    
    async def book_appointment(self, appointment: Dict) -> bool:
        """
        Book the found appointment and fill applicant details
        
        Args:
            appointment: Appointment details from _check_availability
        
        Returns:
            True if booking successful
        """
        try:
            logger.phase("FAZ 3", "Starting appointment booking")
            
            # Click on the appointment slot
            if 'element' in appointment:
                await appointment['element'].click()
                await self.stealth.random_delay(1, 2)
            
            # Fill applicant details
            for idx, applicant in enumerate(self.applicants):
                logger.info(f"Filling details for applicant {idx + 1}: {applicant['first_name']} {applicant['last_name']}")
                await self._fill_applicant_form(applicant, idx)
            
            # Confirm booking
            confirm_button_selectors = [
                'button:has-text("Confirm")',
                'button:has-text("Book")',
                'button:has-text("Onayla")',
                'button:has-text("Rezervasyon Yap")',
                'button[type="submit"]',
                '.btn-confirm',
                '#btnConfirm'
            ]
            
            for selector in confirm_button_selectors:
                try:
                    await self.page.click(selector, timeout=5000)
                    await self.stealth.random_delay(1, 2)
                    break
                except:
                    continue
            
            logger.success("Appointment booked successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error booking appointment: {str(e)}", exc_info=True)
            return False
    
    async def _fill_applicant_form(self, applicant: dict, index: int = 0):
        """Fill form for a single applicant"""
        try:
            # Field mappings
            fields = {
                'first_name': ['input[name*="firstName"]', f'input#firstName{index}', 'input[placeholder*="First Name"]'],
                'last_name': ['input[name*="lastName"]', f'input#lastName{index}', 'input[placeholder*="Last Name"]'],
                'tc_number': ['input[name*="nationalId"]', 'input[name*="tcNo"]', f'input#tcNumber{index}'],
                'passport_number': ['input[name*="passport"]', f'input#passportNumber{index}', 'input[placeholder*="Passport"]'],
                'birth_date': ['input[name*="birthDate"]', 'input[name*="dob"]', f'input#birthDate{index}', 'input[type="date"]'],
                'phone': ['input[name*="phone"]', 'input[name*="mobile"]', f'input#phone{index}', 'input[type="tel"]'],
                'email': ['input[name*="email"]', f'input#email{index}', 'input[type="email"]']
            }
            
            for field_name, selectors in fields.items():
                if field_name in applicant:
                    value = applicant[field_name]
                    
                    for selector in selectors:
                        try:
                            element = await self.stealth.wait_for_element_safely(self.page, selector, timeout=3000)
                            if element:
                                await element.fill('')  # Clear first
                                await self.stealth.human_like_typing(self.page, selector, str(value), delay_range=(0.02, 0.05))
                                logger.debug(f"Filled {field_name}: {value}")
                                break
                        except:
                            continue
            
            await self.stealth.random_delay(0.3, 0.6)
            
        except Exception as e:
            logger.error(f"Error filling applicant form: {str(e)}", exc_info=True)
