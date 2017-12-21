import base64
import getpass

from urllib.parse import urlencode

import click

from rncryptor import RNCryptor
from rncryptor import bord

from bpylist import bplist
from bpylist import archiver
from bpylist.archive_types import uid

import qrcode


class OTPToken:
    secret = None
    issuer = None
    account_name = None
    num_digits = None
    algorithm = None
    unique_id = None
    generation_type = None
    period = None
    counter = None

    def __init__(self, secret, issuer, account_name, num_digits, algorithm,
                 unique_id, generation_type, period, counter):
        self.secret = secret
        self.issuer = issuer
        self.account_name = account_name
        self.num_digits = num_digits
        self.algorithm = algorithm
        self.unique_id = unique_id
        self.generation_type = generation_type
        self.period = period
        self.counter = counter

    def __repr__(self):
        return f'<OTPToken: {self.issuer} ({self.account_name})'

    def encode_archive(self, archive):
        archive.encode('secret', self.secret)
        archive.encode('issuer', self.issuer)
        archive.encode('accountName', self.account_name)
        archive.encode('numDigits', self.num_digits)
        archive.encode('algorithm', self.algorithm)
        archive.encode('uniqueID', self.unique_id)
        archive.encode('type', self.generation_type)
        archive.encode('period', self.period)
        archive.encode('counter', self.counter)

    def decode_archive(archive):
        secret = archive.decode('secret')
        issuer = archive.decode('issuer')
        account_name = archive.decode('accountName')
        num_digits = archive.decode('numDigits')
        algorithm = archive.decode('algorithm')
        unique_id = archive.decode('uniqueID')
        generation_type = archive.decode('type')
        period = archive.decode('period')
        counter = archive.decode('counter')
        return OTPToken(secret, issuer, account_name, num_digits, algorithm,
                        unique_id, generation_type, period, counter)


archiver.update_class_map({'twostepCommon.OTPToken': OTPToken})


class RawRNCryptor(RNCryptor):

    def post_decrypt_data(self, data):
        """Remove useless symbols which
           appear over padding for AES (PKCS#7)."""
        data = data[:-bord(data[-1])]
        return data


class DangerousUnarchive(archiver.Unarchive):

    def decode_object(self, index):
        if index == 0:
            return None

        obj = self.unpacked_uids.get(index)

        if obj is not None:
            return obj

        raw_obj = self.objects[index]

        # if obj is a (semi-)primitive type (e.g. str)
        if not isinstance(raw_obj, dict):
            return raw_obj

        class_uid = raw_obj.get('$class')
        if not isinstance(class_uid, uid):
            raise MissingClassUID(raw_obj)

        klass = self.class_for_uid(class_uid)
        obj = klass.decode_archive(archiver.ArchivedObject(raw_obj, self))

        self.unpacked_uids[index] = obj
        return obj


@click.command()
@click.option('--encrypted-2stp-export',
              help="path to your encrypted 2STP Archive (.2stp)",
              required=True,
              type=click.File('rb'))
def main(encrypted_2stp_export):
    password = getpass.getpass(f'Password for export file {encrypted_2stp_export.name}: ')
    data = RawRNCryptor().decrypt(encrypted_2stp_export.read(), password)
    plist = bplist.parse(data)
    archive = DangerousUnarchive(data).top_object()
    for item in archive:
        otp_type = item.generation_type
        otp_label = f'{item.issuer}:{item.account_name}'
        otp_parameters = {
            'secret': base64.b32encode(item.secret).decode("utf-8"),
            'algorithm': item.algorithm,
            'period': item.period,
            'digits': item.num_digits,
            'issuer': item.issuer,
            'counter': item.counter,
        }
        otp_parameters = urlencode({k: v for k, v in otp_parameters.items() if v})
        otp_uri = f'otpauth://{otp_type}/{otp_label}?{otp_parameters}'
        qr = qrcode.QRCode()
        qr.add_data(otp_uri)
        click.echo("")
        click.echo(f'{item.generation_type}: {item.issuer} - {item.account_name}')
        qr.print_ascii()
        click.echo("")
        input("Press Enter to continue...")


if __name__ == '__main__':
    main()
