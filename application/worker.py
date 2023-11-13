import base64
import hashlib
import hmac
from datetime import datetime
from application.sql_helper import SQLHelper
from core.base_alg_object import BaseAlgObject
from core.pdf_helper import GenerateFromTemplate
from core.token_helper import TokenHelper


def is_correct_password(salt: bytes, pw_hash: bytes, password: str) -> bool:
    """
    Given a previously-stored salt and hash, and a password provided by a user
    trying to log in, check whether the password is correct.
    """
    return hmac.compare_digest(
        pw_hash,
        hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    )


class Worker:
    def __init__(self):
        self.logger = BaseAlgObject.logger
        self.globals = {}

    def init(self):
        self.logger.debug('connecting to the DB')
        # DBInstance.connect()
        self.logger.debug('worker is ready')

    # application api
    # ----------------------------------------
    def get_sms_templates(self) -> list:
        result = SQLHelper.get_all('sms_templates')
        return result

    def get_pdf_templates(self) -> list:
        result = SQLHelper.get_all('pdf_templates')
        return result

    def fill_pdf_templates(self, template_id: int, form_data: dict) -> dict:
        res = SQLHelper.get_by_id('pdf_templates', 'idpdf_templates', template_id)
        gen = GenerateFromTemplate(res['template_data'])

        # for testing purposes
        # gen.draw_grid()

        vehicle_data = form_data['cars']['0']
        users = form_data['users']
        assigned_user = None

        for user in users:
            if f"{user['first_name'].strip()} {user['last_name'].strip()}" == form_data[
                'assignedUserName'] or f"{user['last_name'].strip()} {user['first_name'].strip()}" == form_data[
                'assignedUserName']:
                assigned_user = user

        vehicle_inop = vehicle_data['vehicleInop']
        vehicle_run = None
        if vehicle_inop == 1:
            vehicle_run = 'No'
        else:
            vehicle_run = 'Yes'

        if res['template_name'] == 'Carshipsimple LLC Order Receipt.pdf':
            # For Order Receipt
            # Header
            gen.add_text(form_data['orderId'], (80, 762))  # Order#
            # Shipper Information
            gen.add_text(form_data['customerFullName'], (130, 641))  # Full Name
            gen.add_text("-", (380, 641))  # Company
            gen.add_text(form_data['customerPhone'], (130, 627))  # Phone 1
            gen.add_text(form_data['customerAddress'], (380, 627))  # Address
            gen.add_text(form_data['customerPhone2'], (130, 614))  # Phone 2
            gen.add_text(form_data['customerAddress2'], (380, 614))  # Address 2
            gen.add_text("-", (130, 601))  # Cell
            gen.add_text(form_data['customerCity'], (380, 601))  # City
            gen.add_text("-", (130, 588))  # Fax
            gen.add_text("-", (380, 588))  # State/ZIP
            gen.add_text(form_data['customerEmail'], (130, 574))  # Email
            gen.add_text(form_data['customerCountry'], (380, 574))  # Country
            # Pricing and Shipping
            gen.add_text(form_data['totalTariff'], (320, 495))  # Price Quote
            gen.add_text(form_data['totalBrokerFee'], (320, 482))  # Payments Rec'd
            gen.add_text(form_data['totalTariff'], (320, 470))  # Total Balance
            gen.add_text(form_data['totalBrokerFee'], (320, 457))  # Deposit Due
            gen.add_text(form_data['totalCarrierPay'], (320, 444))  # COD Amount
            gen.add_text(form_data['firstPickupDate'], (315, 432))  # 1st Avail Date
            gen.add_text(form_data['PickupDate'], (315, 419))  # Est. Pickup Date
            gen.add_text(form_data['DeliveryDate'], (315, 406))  # Est. Delivery Date
            gen.add_text(form_data['shipVia'], (315, 393))  # Ship Via
            gen.add_text(vehicle_run, (315, 381))  # Vehicle(s) Run
            # Payment Received
            gen.add_text("Payment Received", (100, 328))  # Payment Received status
            # Transit Directives
            gen.add_text(form_data['originContactName'], (130, 247))  # Origin Name
            gen.add_text(form_data['destinationContactName'], (380, 247))  # Destination Name
            gen.add_text(form_data['originCompanyName'], (130, 234))  # Origin Company
            gen.add_text(form_data['destinationCompanyName'], (380, 234))  # Destination Company
            gen.add_text(form_data['originContactPhone'], (130, 221))  # Origin Phone 1
            gen.add_text(form_data['destinationContactPhone'], (380, 221))  # Destination Phone 1
            gen.add_text(form_data['originAddress'], (130, 207))  # Origin Address
            gen.add_text(form_data['destinationAddress'], (380, 207))  # Destination Address
            gen.add_text(form_data['originAddress2'], (130, 194))  # Origin Address 2
            gen.add_text(form_data['destinationAddress2'], (380, 194))  # Destination Address 2
            gen.add_text(form_data['originCity'], (130, 180))  # Origin City
            gen.add_text(form_data['destinationCity'], (380, 180))  # Destination City
            gen.add_text(f"{form_data['originState']} {form_data['originZip']}", (130, 167))  # Origin State/Zip
            gen.add_text(f"{form_data['destinationState']} {form_data['destinationZip']}",
                         (380, 167))  # Destination State/Zip
            gen.add_text(form_data['originCountry'], (130, 153))  # Origin Country
            gen.add_text(form_data['destinationCountry'], (380, 153))  # Destination Country
            # Vehicle Information
            gen.add_text(
                f"{vehicle_data['vehicleModelYear']} {vehicle_data['vehicleMake']} {vehicle_data['vehicleModel']}",
                (43, 105))  # Year/Make/Model
            gen.add_text(vehicle_data['vehicleType'], (223, 105))  # Type
            gen.add_text("-", (261, 105))  # Color
            gen.add_text(vehicle_data['vehiclePlateNumber'], (293, 105))  # Lic. Plate
            gen.add_text(vehicle_data['vehicleVin'], (336, 105))  # VIN
            gen.add_text(vehicle_data['vehicleLotNumber'], (422, 105))  # Lot#
            gen.add_text(form_data['totalTariff'], (500, 105))  # Tariff

        elif res['template_name'] == 'Carshipsimple LLC Shipping Order Form.pdf':
            # For Shipping Order Form
            # Header
            gen.add_text(form_data['assignedUserName'], (295, 632))  # Agent
            gen.add_text(assigned_user['phone'], (295, 618))  # Phone
            gen.add_text(assigned_user['email'], (295, 605))  # Email
            # Shipper Information
            gen.add_text(form_data['customerFullName'], (130, 527))  # Full Name
            gen.add_text("-", (380, 527))  # Company
            gen.add_text(form_data['customerPhone'], (130, 514))  # Phone 1
            gen.add_text(form_data['customerAddress'], (380, 514))  # Address
            gen.add_text(form_data['customerPhone2'], (130, 501))  # Phone 2
            gen.add_text(form_data['customerAddress2'], (380, 501))  # Address 2
            gen.add_text("-", (130, 488))  # Cell
            gen.add_text(form_data['customerCity'], (380, 488))  # City
            gen.add_text("-", (130, 474))  # Fax
            gen.add_text("-", (380, 474))  # State/ZIP
            gen.add_text(form_data['customerEmail'], (130, 461))  # Email
            gen.add_text(form_data['customerCountry'], (380, 461))  # Country
            # Pricing and Shipping
            gen.add_text(form_data['orderId'], (315, 380))  # Order Number
            gen.add_text(form_data['totalTariff'], (320, 368))  # Calculated Rate
            gen.add_text(form_data['firstPickupDate'], (315, 355))  # 1st Avail Date
            gen.add_text(form_data['shipVia'], (315, 342))  # Ship Via
            gen.add_text(vehicle_run, (315, 330))  # Vehicle(s) Run
            # Transit Directives
            gen.add_text(form_data['originContactName'], (130, 237))  # Origin Name
            gen.add_text(form_data['destinationContactName'], (380, 237))  # Destination Name
            gen.add_text(form_data['originCompanyName'], (130, 224))  # Origin Company
            gen.add_text(form_data['destinationCompanyName'], (380, 224))  # Destination Company
            gen.add_text(form_data['originContactPhone'], (130, 211))  # Origin Phone 1
            gen.add_text(form_data['destinationContactPhone'], (380, 211))  # Destination Phone 1
            gen.add_text(form_data['originAddress'], (130, 197))  # Origin Address
            gen.add_text(form_data['destinationAddress'], (380, 197))  # Destination Address
            gen.add_text(form_data['originAddress2'], (130, 184))  # Origin Address 2
            gen.add_text(form_data['destinationAddress2'], (380, 184))  # Destination Address 2
            gen.add_text(form_data['originCity'], (130, 171))  # Origin City
            gen.add_text(form_data['destinationCity'], (380, 171))  # Destination City
            gen.add_text(f"{form_data['originState']} {form_data['originZip']}", (130, 157))  # Origin State/Zip
            gen.add_text(f"{form_data['destinationState']} {form_data['destinationZip']}",
                         (380, 157))  # Destination State/Zip
            gen.add_text(form_data['originCountry'], (130, 144))  # Origin Country
            gen.add_text(form_data['destinationCountry'], (380, 144))  # Destination Country
            # Vehicle Information
            gen.add_text(
                f"{vehicle_data['vehicleModelYear']} {vehicle_data['vehicleMake']} {vehicle_data['vehicleModel']}",
                (43, 96))  # Year/Make/Model
            gen.add_text(vehicle_data['vehicleType'], (223, 96))  # Type
            gen.add_text("-", (261, 96))  # Color
            gen.add_text(vehicle_data['vehiclePlateNumber'], (293, 96))  # Lic. Plate
            gen.add_text(vehicle_data['vehicleVin'], (336, 96))  # VIN
            gen.add_text(vehicle_data['vehicleLotNumber'], (422, 96))  # Lot#
            gen.add_text(form_data['totalTariff'], (500, 96))  # Tariff

        gen.merge()

        # for testing purposes
        # gen.generate("Output.pdf")

        generated_bytes = gen.return_bytes()
        encoded_file = base64.b64encode(generated_bytes)
        res['template_data'] = encoded_file.decode()
        return res

    def create_user(self, user_data: dict) -> dict:
        password = user_data.pop('password')
        user_data['create_date'] = datetime.now()
        result = SQLHelper.create_user(user_data, password)
        if result['status'] != 'ok':
            return result
        else:
            response = result['result']
            response.pop('password_hash')
            response.pop('password_salt')
            return response

    def login(self, username: str, password: str) -> dict:
        response = SQLHelper.get_user_by_username(username)
        if response['status'] != 'ok':
            return {'status': 'error', 'message': response['message']}
        else:
            user = response['result']
            db_salt = user['password_salt']
            db_hash = user['password_hash']
            if not is_correct_password(db_salt, db_hash, password):
                return {'status': 'error', 'message': 'Wrong password'}
            else:
                token = TokenHelper.create_token(user)
                logged_in_user = {
                    'username': user['username'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'phone': user['phone'],
                    'contact_email': user['contact_email']
                }
                return {'status': 'ok', 'user': logged_in_user, 'token': token}

    def update_token(self, username: str) -> dict:
        response = SQLHelper.get_user_by_username(username)
        if response['status'] != 'ok':
            return {'status': 'error', 'message': response['message']}
        else:
            user = response['result']
            token = TokenHelper.create_token(user)
            return {'status': 'ok', 'token': token}

    def create_pdf_template(self, file_name: str, file_bytes: bytes) -> dict:
        result = SQLHelper.create_pdf_template(file_name, file_bytes)
        return result
