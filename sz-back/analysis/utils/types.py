from dataclasses import dataclass

@dataclass
class PageToken:
    text: str
    x0: float; y0: float; x1: float; y1: float
    page_index: int
    start_offset: int
    end_offset: int
