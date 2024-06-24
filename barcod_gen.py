import barcode
from barcode.writer import ImageWriter


async def generate_barcode(code, barcode_type, dpi=300, module_width=0.2):
    ITF = barcode.get_barcode_class(barcode_type)
    itf = ITF(code, writer=ImageWriter())
    filename = f'{code}.{barcode_type}'
    itf.save(filename, options={"dpi": dpi, "module_width": module_width})



