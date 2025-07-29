import requests
import sqlite3
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, timedelta
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE = 'crossword_data.db'

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def scrape_word(href):
    url = f"https://www.xwordinfo.com{href}"
    cookies = {
        'ASP.NET_SessionId': 'pqaw25q3p53vxgn30uhjero1',
        'wv': '-1',
        '_clck': '1weutu7%7C2%7Cfy0%7C0%7C2036',
        '_ga': 'GA1.1.688573605.1753762597',
        '__gads': 'ID=fd8d22595b67f943:T=1753762598:RT=1753762598:S=ALNI_MYGC16fYWq_-zYauew4GlFhecKASQ',
        '__gpi': 'UID=000010fe77b25067:T=1753762598:RT=1753762598:S=ALNI_MZUr0obtcPZh4nvJVMvqwL7TlNJ4Q',
        '__eoi': 'ID=1e0aa4aeed4d96e4:T=1753762598:RT=1753762598:S=AA-AfjZSWXeG4G84a24OR7TYoxry',
        'Verify': 'stamp=7/28/2025 9:16:40 PM&pages=2',
        '_clsk': '1p8j6zj%7C1753762620812%7C6%7C1%7Ci.clarity.ms%2Fcollect',
        '_ga_4N9YZGECSH': 'GS2.1.s1753762596$o1$g1$t1753762621$j35$l0$h0',
        'FCNEC': '%5B%5B%22AKsRol9jR4TKKMUnTOo77ZNzhGHDlArmGrCKu_P5pn5nm5OLq_QtvFmEQ3InGUXhPLL_ZwWtOPEG-DNNuvxiPpkXAwgferbyzBvmCHIz4jy3JhcmyQ8w8xEeT_i8wnmpJro5tv9N4s3yw-lOHGRUhbKifCc6LPi90A%3D%3D%22%5D%5D',
        '.AspNet.ApplicationCookie': 'VW2lJmNDkdCcr5161dJJuVdhPBbY3zVmbS3Xk9lMxm69YJ2PmuGqf-vv3AO6TqK2XxUqKhYsYgX9UT5r14sxCTVEJbNOibNcf6TPrtBP53AYGDyaLvg2A6K6oggyz9nwt4szmPiPg6GE_OgWRJ3kQl-3lS3vxHAb2pJDbDhlBmU9vJP3pGr4FVFuFIE652w6Szvv8UfEJFV53cUBxoYFZzairwjHU_26nKJwFG1WNv8MYOpqI3l73IGcaHm14m_eVZirKXe0qGfDUr20maApwa_SZlP0HlC2v2GhW9tOXI65jENjEC30xpgI_nVNEBf9gFUWoBMFdXNa38NlNmsadFwfw8SxMGs-XFT4iYs7dfDoviYSs4A2naf1AFaTAcf7uXn5nndttodjCQZY-3hDEbd4PYMMJCK7RZq9ATKsawuRiquVDjD3WiAV5LJ0_n75YHmvzXm1OLnujd3APpApovBv0DxzbEdk011ogTtY5hsq6SNf8XqIhJOEJBM4XpH1',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://www.xwordinfo.com/Account/Login.aspx?ReturnUrl=%2fFinder%3fw%3dORE',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        # 'cookie': 'ASP.NET_SessionId=pqaw25q3p53vxgn30uhjero1; wv=-1; _clck=1weutu7%7C2%7Cfy0%7C0%7C2036; _ga=GA1.1.688573605.1753762597; __gads=ID=fd8d22595b67f943:T=1753762598:RT=1753762598:S=ALNI_MYGC16fYWq_-zYauew4GlFhecKASQ; __gpi=UID=000010fe77b25067:T=1753762598:RT=1753762598:S=ALNI_MZUr0obtcPZh4nvJVMvqwL7TlNJ4Q; __eoi=ID=1e0aa4aeed4d96e4:T=1753762598:RT=1753762598:S=AA-AfjZSWXeG4G84a24OR7TYoxry; Verify=stamp=7/28/2025 9:16:40 PM&pages=2; _clsk=1p8j6zj%7C1753762620812%7C6%7C1%7Ci.clarity.ms%2Fcollect; _ga_4N9YZGECSH=GS2.1.s1753762596$o1$g1$t1753762621$j35$l0$h0; FCNEC=%5B%5B%22AKsRol9jR4TKKMUnTOo77ZNzhGHDlArmGrCKu_P5pn5nm5OLq_QtvFmEQ3InGUXhPLL_ZwWtOPEG-DNNuvxiPpkXAwgferbyzBvmCHIz4jy3JhcmyQ8w8xEeT_i8wnmpJro5tv9N4s3yw-lOHGRUhbKifCc6LPi90A%3D%3D%22%5D%5D; .AspNet.ApplicationCookie=VW2lJmNDkdCcr5161dJJuVdhPBbY3zVmbS3Xk9lMxm69YJ2PmuGqf-vv3AO6TqK2XxUqKhYsYgX9UT5r14sxCTVEJbNOibNcf6TPrtBP53AYGDyaLvg2A6K6oggyz9nwt4szmPiPg6GE_OgWRJ3kQl-3lS3vxHAb2pJDbDhlBmU9vJP3pGr4FVFuFIE652w6Szvv8UfEJFV53cUBxoYFZzairwjHU_26nKJwFG1WNv8MYOpqI3l73IGcaHm14m_eVZirKXe0qGfDUr20maApwa_SZlP0HlC2v2GhW9tOXI65jENjEC30xpgI_nVNEBf9gFUWoBMFdXNa38NlNmsadFwfw8SxMGs-XFT4iYs7dfDoviYSs4A2naf1AFaTAcf7uXn5nndttodjCQZY-3hDEbd4PYMMJCK7RZq9ATKsawuRiquVDjD3WiAV5LJ0_n75YHmvzXm1OLnujd3APpApovBv0DxzbEdk011ogTtY5hsq6SNf8XqIhJOEJBM4XpH1',
    }

    response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
    response.raise_for_status()
    print(response.status_code)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find_all('table')[2]
    rows = table.find_all('tr')
    data_out=[]
    for row in rows:
        cells = row.find_all('td')
        answer = href.split('?w=')[1]
        if(len(cells) < 5):
            continue
        date =  cells[0].text.strip()
        clue = cells[2].text.strip()
        m = re.search(r'\(\d+\)', clue)
        occurrences = '1'
        if m:
            occurrences = m.group(0)[1:-1]
            clue = clue.replace(m.group(0), '')
        clue = clue.strip()
        author = cells[3].text.strip()
        editor = cells[4].text.strip()
        data_out.append({'answer':answer, 'date':date, 'clue':clue, 'author':author, 'editor':editor, 'occurrences':occurrences})
    return data_out

def scrape_xwordinfo_crossword(date_str):
    """Scrape crossword data from XWord Info for a specific date"""
    logger.info(f"Starting XWord Info scraping for date: {date_str}")
    
    # XWord Info URL format
    url = f"https://www.xwordinfo.com/Crossword?date={date_str}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        clues_data = []
        
        # Extract author and editor information

        a_list = soup.find_all('a')
        for a in a_list:
            if a.get('href', '').startswith('/Finder?w='):
                print(a.get('href'))
                clues_data.extend(scrape_word(a.get('href')))
        
        logger.info(f"Scraped {len(clues_data)} clues from XWord Info for {date_str}")
        return clues_data
        
    except Exception as e:
        logger.error(f"Error scraping XWord Info for {date_str}: {str(e)}")
        return []

def scrape_recent_crosswords(days_back=1):
    """Scrape recent crosswords from XWord Info"""
    logger.info(f"Starting to scrape {days_back} days of crosswords from XWord Info")
    
    all_clues = []
    base_date = datetime.now()
    
    for i in range(days_back):
        # Calculate the date to scrape
        target_date = base_date - timedelta(days=i)
        date_str = target_date.strftime('%-m/%-d/%Y')  # Format: 7/22/2025
        
        try:
            clues = scrape_xwordinfo_crossword(date_str)
            all_clues.extend(clues)
            
            # Be respectful - add delay between requests
            time.sleep(random.uniform(2, 4))
            
            logger.info(f"Completed scraping for {date_str}")
            
        except Exception as e:
            logger.error(f"Error scraping {date_str}: {str(e)}")
            continue
    
    return all_clues


def save_to_database(clues_data):
    """Save scraped clues to the database"""
    if not clues_data:
        logger.info("No clues to save")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    count = 0
    
    try:
        for clue in clues_data:
            # Check if this clue already exists
            cursor.execute('''
                SELECT id FROM crossword_clues 
                WHERE UPPER(answer) = UPPER(?) AND UPPER(clue) = UPPER(?) AND UPPER(date) = UPPER(?)
            ''', (clue['answer'], clue['clue'], clue['date']))
            
            existing = cursor.fetchone()
            if existing:
                count+=1
            else:
                # Insert new clue
                cursor.execute('''
                    INSERT INTO crossword_clues (answer, clue, date, author, editor, occurrences)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    clue['answer'],
                    clue['clue'],
                    clue['date'],
                    clue['author'],
                    clue['editor'],
                    clue['occurrences']
                ))
        conn.commit()
        logger.info(f"Successfully saved {len(clues_data) - count} clues to database")
        
    except Exception as e:
        logger.error(f"Error saving to database: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def run_daily_scraping():
    """Run the daily scraping process"""
    logger.info("Starting daily crossword scraping process...")
    
    all_clues = []

    try:
        clues = scrape_recent_crosswords(days_back=1)
        all_clues.extend(clues)
        
    except Exception as e:
        logger.error(f"Error with XWord Info scraping: {str(e)}")
    
    
    # Save all collected clues to database
    save_to_database(all_clues)
    
    logger.info(f"Daily scraping completed. Total clues processed: {len(all_clues)}")

if __name__ == "__main__":
    run_daily_scraping() 