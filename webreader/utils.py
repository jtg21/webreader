from typing import Dict, Any

def format_website_data(website_data: Dict[str, Any]) -> str:
    formatted_content = ""
    
    for url, content in website_data.items():
        formatted_content += f"Website URL: {url}\n"
        formatted_content += f"Title: {content.get('title', 'N/A').strip()}\n"
        
        formatted_content += "Headings:\n"
        for heading in content.get('headings', []):
            formatted_content += f"  - {heading.strip()}\n"
        
        formatted_content += "Paragraphs:\n"
        for paragraph in content.get('paragraphs', []):
            # Remove extra newlines and whitespace within paragraphs
            cleaned_paragraph = ' '.join(paragraph.split())
            formatted_content += f"  {cleaned_paragraph}\n"
        
        formatted_content += "Lists:\n"
        for lst in content.get('lists', []):
            formatted_content += f"  - {' '.join(lst.split())}\n"
        formatted_content += "-"*80 + "\n"
    
    return formatted_content

