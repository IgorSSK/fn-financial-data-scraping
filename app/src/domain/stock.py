from datetime import datetime
from typing import List

class Quote:
  percent_change: float
  price_change: float
  price: float
  currency: str
  technical_rating: str
  quoted_at: datetime

class Stock: 
  name: str
  symbol: str
  company_img: str
  company_shortcut: str
  exchange: str
  sector: str
  quote: Quote
  