#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class Flight:
    destination: str
    departure_date: int
    aircraft_type: str


@dataclass
class FlightManager:
    file_path: Path
    flights: List[Flight] = field(default_factory=list)

    def add_flight(
        self, destination: str, departure_date: int, aircraft_type: str
    ) -> None:
        self.flights.append(Flight(destination, departure_date, aircraft_type))

    def display_flights(self) -> None:
        if self.flights:
            header_line = "+-{}-+-{}-+-{}-+-{}-+".format(
                "-" * 4, "-" * 30, "-" * 20, "-" * 8
            )
            print(header_line)
            print(
                "| {:^4} | {:^30} | {:^20} | {:^8} |".format(
                    "No", "Destination", "Departure Date", "Aircraft Type"
                )
            )
            print(header_line)
            for idx, flight in enumerate(self.flights, 1):
                print(
                    "| {:>4} | {:<30} | {:<20} | {:>8} |".format(
                        idx,
                        flight.destination,
                        flight.departure_date,
                        flight.aircraft_type,
                    )
                )
                print(header_line)
        else:
            print("No flights found.")

    def select_flights(self, date: int) -> List[Flight]:
        return [
            flight for flight in self.flights if flight.departure_date == date
        ]

    def save_flights_json(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as fout:
            json_dump = [flight.__dict__ for flight in self.flights]
            json.dump(json_dump, fout, ensure_ascii=False, indent=4)

    def load_flights_json(self) -> None:
        with open(self.file_path, "r", encoding="utf-8") as fin:
            data = json.load(fin)
            self.flights = [Flight(**flight_data) for flight_data in data]

    def save_flights_xml(self) -> None:
        root = ET.Element("flights")
        for flight in self.flights:
            flight_element = ET.SubElement(root, "flight")
            ET.SubElement(flight_element, "destination").text = (
                flight.destination
            )
            ET.SubElement(flight_element, "departure_date").text = str(
                flight.departure_date
            )
            ET.SubElement(flight_element, "aircraft_type").text = (
                flight.aircraft_type
            )
        tree = ET.ElementTree(root)
        with open(self.file_path, "wb") as fout:
            tree.write(fout, encoding="utf-8", xml_declaration=True)


def main(command_line=None) -> None:
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "filename", action="store", help="The data file name"
    )

    parser = argparse.ArgumentParser("flights")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    subparsers = parser.add_subparsers(dest="command")

    add = subparsers.add_parser(
        "add", parents=[file_parser], help="Add a new flight"
    )
    add.add_argument(
        "-d",
        "--destination",
        action="store",
        required=True,
        help="Destination of the flight",
    )
    add.add_argument(
        "-dd",
        "--departure_date",
        action="store",
        required=True,
        help="Departure date of the flight",
    )
    add.add_argument(
        "-at",
        "--aircraft_type",
        action="store",
        required=True,
        help="Aircraft type of the flight",
    )

    _ = subparsers.add_parser(
        "display", parents=[file_parser], help="Display all flights"
    )

    select = subparsers.add_parser(
        "select", parents=[file_parser], help="Select flights by departure date"
    )
    select.add_argument(
        "-D",
        "--date",
        action="store",
        required=True,
        help="Departure date to select flights",
    )

    args = parser.parse_args(command_line)

    home_dir = Path.home()
    file_path = home_dir / args.filename

    flight_manager = FlightManager(file_path)

    if args.command == "add":
        flight_manager.add_flight(
            args.destination, int(args.departure_date), args.aircraft_type
        )

    elif args.command == "display":
        flight_manager.display_flights()

    elif args.command == "select":
        selected_flights = flight_manager.select_flights(int(args.date))
        flight_manager.display_flights(selected_flights)

    if args.command in ("add", "display", "select"):
        if file_path.suffix == ".json":
            flight_manager.save_flights_json()
        elif file_path.suffix == ".xml":
            flight_manager.save_flights_xml()


if __name__ == "__main__":
    main()
