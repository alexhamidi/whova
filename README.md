# Event Agenda Manager

Simple command-line tool to import and search event agendas from Excel files.

## Features
- Import event schedules from Excel files into SQLite database
- Search sessions by date, time, title, location, description or speaker
- Handles both sessions and subsessions
- Tracks speaker information

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Import an Agenda
```bash
python import_agenda.py agenda.xls
```

### Search the Agenda
```bash
python lookup_agenda.py <column> <value>
```

Where column can be:
- date
- time_start
- time_end
- title
- location
- description
- speaker

Example:
```bash
python lookup_agenda.py location "Main Hall"
python lookup_agenda.py speaker "John Smith"
```

## Excel File Format
See the provided `agenda.xls` for the expected format. The Excel file should have the following columns:
- Date
- Time Start
- Time End
- Title
- Location
- Description
- Speaker(s)
- Session Type (Session/Sub)
