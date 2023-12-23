from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
from RPA.FileSystem import FileSystem

@task
def ordenes_robot():
    """Realiza pedidos de robots a RobotSpareBin Industries Inc.
     Guarda el recibo HTML del pedido como un archivo PDF.
     Guarda la captura de pantalla del robot solicitado.
     Incrusta la captura de pantalla del robot en el recibo PDF.
     Crea un archivo ZIP de los recibos y las imágenes."""
    browser.configure(
        slowmo=100,
    )
    abrir_navegador()
    descargar_archivo()
    orders = leer_tabla()
    for row in orders:
        renunciar_derechos()
        rellenar_formulario(row)
        exportar_pdf(str(row["Order Number"]))
    archivos_recibidos()

def abrir_navegador():
    """Abrir el navegador de pedidos"""
    browser.goto(url="https://robotsparebinindustries.com/#/robot-order")

def renunciar_derechos():
    """Renunciar a derechos al abrir la pagina"""
    page = browser.page()
    page.click("button:text('OK')")

def descargar_archivo():
    """Descargar"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

def leer_tabla():
    """Leer información de la tabla"""
    orders= Tables().read_table_from_csv("orders.csv", columns=["Order number","Head","Body","Legs","Address"])
    return orders
def rellenar_formulario(order):
    """Completar formulario con info de la tabla"""
    page = browser.page()

    page.select_option("#head", str(order["Head"]))
    page.click("#id-body-"+str(order["Body"]))
    leg_id = page.get_attribute("label:text('3. Legs:')","for")
    page.fill("input[id='"+ leg_id +"']", str(order["Legs"]))
    page.fill("#address", str(order["Address"]))
    page.click("button:text('Preview')")
    
    while(page.query_selector("#receipt")is None):
        page.click("button:text('Order')")

def exportar_pdf(order_number):
    page = browser.page()
    localizador_pdf_html = page.locator("#receipt").inner_html(timeout=10)
    
    pdf = PDF()
    lib = FileSystem()
    lib.create_directory("output/recibos"
    )
    pdf.html_to_pdf(localizador_pdf_html,"output/recibos/ejemplo.pdf")

    pantallazo_recibo(order_number)

    añadir_screenshot("output/recibos"+order_number+"png")

    page.click("button:text('Order another robot')")
    
def pantallazo_recibo(order_number):
    """Realizar captura de pantalla"""
    page = browser.page()
    localizador_pantallazo = page.locator("#receipt").inner_html()

    page.screenshot(localizador_pantallazo, path="output/recibos/pantallazo.png")


def añadir_screenshot(screenshot, pdf_file):
    
    list_of_files = [
        screenshot +':align=center'
    ]
    pdf = PDF()
    pdf.open_pdf(pdf_file)
    pdf.add_files_to_pdf(files=list_of_files,target_document=pdf_file,append=True)
    pdf.save_pdf(output_path=pdf_file)
    pdf.close_all_pdfs()

def archivos_recibidos():
    lib = Archive()
    lib.archive_folder_with_zip("output/recibos", "recibidos.zip")
