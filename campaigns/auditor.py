import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import os

class WebsiteAuditor:
    def __init__(self, url, role_config=None):
        """
        role_config: dict with keys like 'ux', 'marketing', 'conversion', 'automation'
        """
        self.url = url
        self.role_config = role_config or {'ux': True, 'conversion': True}
        self.html_content = ""
        self.screenshot_path = ""

    async def run_audit(self):
        results = {"url": self.url, "findings": {}}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto(self.url, wait_until="networkidle", timeout=30000)
                self.html_content = await page.content()
                
                # Take screenshot for UX analysis
                os.makedirs("media/audits", exist_ok=True)
                safe_url = self.url.replace("https://", "").replace("http://", "").replace("/", "_")
                self.screenshot_path = f"media/audits/{safe_url}.png"
                await page.screenshot(path=self.screenshot_path)
                
                soup = BeautifulSoup(self.html_content, 'html.parser')
                
                if self.role_config.get('ux'):
                    results['findings']['ux'] = self._audit_ux(page, soup)
                
                if self.role_config.get('conversion'):
                    results['findings']['conversion'] = self._audit_conversion(soup)
                    
                if self.role_config.get('marketing'):
                    results['findings']['marketing'] = self._audit_marketing(soup)
                    
            except Exception as e:
                results['error'] = str(e)
            finally:
                await browser.close()
        
        return results

    def _audit_ux(self, page, soup):
        # Basic UX checks
        has_mobile_meta = bool(soup.find("meta", attrs={"name": "viewport"}))
        linksCount = len(soup.find_all('a'))
        images_without_alt = len([img for img in soup.find_all('img') if not img.get('alt')])
        
        return {
            "mobile_friendly": has_mobile_meta,
            "images_missing_alt": images_without_alt,
            "total_links": linksCount,
            "complexity": "High" if linksCount > 100 else "Normal"
        }

    def _audit_conversion(self, soup):
        # Conversion checks
        ctas = [a.text.strip() for a in soup.find_all('a') if any(word in a.text.lower() for word in ['get started', 'sign up', 'book', 'demo', 'contact'])]
        has_form = bool(soup.find('form'))
        
        return {
            "cta_found": bool(ctas),
            "cta_count": len(ctas),
            "primary_cta": ctas[0] if ctas else None,
            "has_contact_form": has_form
        }

    def _audit_marketing(self, soup):
        # Marketing checks
        has_fb_pixel = 'facebook-jssdk' in self.html_content or 'fbevents.js' in self.html_content
        has_gtm = 'googletagmanager.com' in self.html_content
        
        return {
            "facebook_pixel": has_fb_pixel,
            "google_tag_manager": has_gtm,
            "seo_title": soup.title.string if soup.title else "Missing",
            "h1_count": len(soup.find_all('h1'))
        }

# Usage:
# auditor = WebsiteAuditor("https://example.com", {'ux': True, 'marketing': True})
# results = asyncio.run(auditor.run_audit())
