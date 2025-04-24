import csv
import os
import pprint
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile

from django.core.management.base import BaseCommand

from extras.data.iso_3166 import ISO_3166


class Command(BaseCommand):
    help = "Import UN/LOCODE codes from the UNECE source data set and regenerate UN_LOCODES ChoiceSet values"
    subdivisions = {}
    countries = {}
    code_list = []
    subdivisions_file = None
    code_list_files = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            help="URL of CSV file archive (.zip) to download",
            dest='url',
            required=True,
        )
        parser.add_argument(
            '--extract-to',
            help="Directory to extract unzipped CSV files to (will create if necessary)",
            dest='extract_to',
            default=".",
        )

    def handle(self, *args, **options):
        url = options['url']
        extract_to = options['extract_to']

        http_response = urlopen(url)
        zipfile = ZipFile(BytesIO(http_response.read()))
        zipfile.extractall(path=extract_to)

        for country_code, country_name in ISO_3166:
            self.countries[country_code] = country_name[4:-1]

        for file in sorted(os.listdir(extract_to)):
            if "SubdivisionCodes" in file:
                self.subdivisions_file = os.path.join(extract_to, file)
            elif "CodeList" in file:
                self.code_list_files.append(os.path.join(extract_to, file))

        with open(self.subdivisions_file, mode='r', encoding='cp1252') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                key = f"{row[0]}-{row[1]}"
                self.subdivisions[key] = row[2]

        locodes = []
        for code_list_file in self.code_list_files:
            with open(code_list_file, mode='r', encoding='cp1252') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if not row[2]:
                        continue
                    key = f"{row[1]}-{row[2]}"
                    subdivision_key = f"{row[1]}-{row[5]}"
                    value_str = row[3]
                    if subdivision := self.subdivisions.get(subdivision_key, ""):
                        value_str = f"{value_str}, {subdivision}"
                    country = self.countries.get(row[1])
                    value_str = f"{value_str}, {country}"
                    value = f"{key} ({value_str})"
                    locodes.append((key, value))

        pprint.pprint(tuple(locodes))
