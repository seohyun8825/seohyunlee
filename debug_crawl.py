#!/usr/bin/env python3
"""
Debug script to analyze Tistory structure
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_tistory():
    url = "https://happy8825.tistory.com/"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    try:
        response = session.get(url)
        response.raise_for_status()
        html = response.text
        
        soup = BeautifulSoup(html, 'html.parser')
        
        print("=== TISTORY STRUCTURE ANALYSIS ===")
        print(f"Title: {soup.title.string if soup.title else 'No title'}")
        
        # Look for all links
        print("\n=== ALL LINKS ===")
        links = soup.find_all('a', href=True)
        for i, link in enumerate(links[:20]):  # Show first 20 links
            href = link.get('href', '')
            text = link.get_text().strip()
            if text and len(text) > 3:  # Only show meaningful links
                print(f"{i+1}. {text[:50]} -> {href}")
        
        # Look for specific patterns
        print("\n=== ENTRY/POST LINKS ===")
        entry_links = [link for link in links if '/entry/' in link.get('href', '') or '/post/' in link.get('href', '')]
        for link in entry_links:
            print(f"Entry: {link.get_text().strip()} -> {link.get('href')}")
        
        # Look for article/div containers
        print("\n=== ARTICLE/DIV CONTAINERS ===")
        containers = soup.find_all(['article', 'div'])
        for i, container in enumerate(containers[:10]):
            classes = container.get('class', [])
            if classes:
                print(f"Container {i+1}: {classes}")
                # Look for links inside
                inner_links = container.find_all('a', href=True)
                for link in inner_links:
                    if '/entry/' in link.get('href', ''):
                        print(f"  -> Entry link: {link.get_text().strip()}")
        
        # Save HTML for manual inspection
        with open('tistory_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\nHTML saved to tistory_debug.html for manual inspection")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_tistory()
