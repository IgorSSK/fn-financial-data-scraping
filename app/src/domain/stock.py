from datetime import datetime
from typing import List

class Price:
  quotedAt: datetime
  percent_change: float
  price_change: float
  price: float
  currency: str
  technical_rating: str

class Stock: 
  name: str
  symbol: str
  company_img: str
  company_shortcut: str
  exchange: str
  currency: str
  technical_rating: str
  price: List[Price]
  