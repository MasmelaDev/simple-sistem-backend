from fastapi import FastAPI
from pydantic import BaseModel
from escpos.printer import Usb
import locale
import json
app = FastAPI()

# ticket model

class TicketData(BaseModel):
    name: str
    phone: str
    saleType: str
    street: str
    number: str
    neighborhoodName: str
    delivery: str
    deliveryPrice:str
    observations: str
    productsInSale: str

try:
        c = Usb(0x0483, 0x5720)
except Exception as e:
                print("error","no se pudo conectar la impresora, verifica que este conectada y encendida",e)


# Establecer la configuración local para Colombia
locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')

# Función para formatear el precio
def format_price(price):
    return locale.currency(price, symbol=None, grouping=True)





@app.post("/printTicket")
async def printTicket(ticketData:TicketData):
   # Convertir el string JSON en un array de objetos Python
    productsInSaleData = json.loads(ticketData.productsInSale)
    total = 0
    
    for productInSale in productsInSaleData:
        total += productInSale["total"]
    # Imprimir los datos
    c.set(align="center",bold=True,width=2,height=2,custom_size=True)
    c.image("./img.png")
    c.text(f'Sandcibatta\n')
    c.ln(2)
    c.set(align="left")
    c.text(f'Telefono: ')
    c.set(bold=False)
    c.text(f'{ticketData.phone}\n')
    c.set(bold=True)
    c.text('Cliente: ')
    c.set(bold=False)
    c.text(f'{ticketData.name}\n')
    c.set(bold=True)
    c.text('Direccion: ')
    c.set(bold=False)
    c.text(f'{ticketData.street} # {ticketData.number} \n')
    c.set(bold=True)
    c.text('Barrio: ')
    c.set(bold=False)
    c.text(f'{ticketData.neighborhoodName}\n')
    c.ln(1)
    c.set(align="center",bold=True)
    c.text('________________________________________________\n')
    c.ln(1)
    c.set(align="center",width=2,height=2,custom_size=True)
    for productInSale in productsInSaleData:
        c.text(f'{productInSale["amount"]} {productInSale["product"]["name"]} ${format_price(productInSale["total"])}\n')
    c.ln(3)
    c.set(align="right",bold=True)
    c.text('SUBTOTAL: ')
    c.set(align="right",bold=False)
    c.text(f'  $ {format_price(total)}\n')
    c.set(align="right",bold=True)
    c.text('Valor Domicilio: ')
    c.set(align="right",bold=False)
    c.text(f'   $ {format_price(int(ticketData.deliveryPrice))}\n')
    c.set(align="right",bold=True)
    c.text('TOTAL: ')
    c.set(align="right",bold=False)
    c.text(f'  $ {format_price(total + int(ticketData.deliveryPrice))} \n')
    c.cut()
    if ticketData.observations !="":
            c.set(align="center",width=2,height=2,custom_size=True)
            c.text(f'{ticketData.observations}\n')
            c.cut()
    return {"message": "Ticket printed successfully!"}

