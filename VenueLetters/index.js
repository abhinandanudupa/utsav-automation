import { parse } from 'csv-parse';
import { createReadStream, writeFileSync } from 'node:fs';

import docx from 'docx';
const { Packer } = docx;

import { generateVenueLettersForDepartment } from './generate_letter.js';
import { padSerial } from './utils.js';

const CSV_FILE = './allotments.csv';

const ignoreEmptyRecords = (record, { lines }) => {
  const fields = Object.keys(record);

  return record[fields[2]] !== '' ? record : null;
};

const processFile = async (fileToProcess) => {
  const records = [];
  const parser = createReadStream(fileToProcess).pipe(
    parse({
      columns: true,
      trim: true,
      on_record: ignoreEmptyRecords,
    })
  );
  for await (const record of parser) {
    records.push(record);
  }
  // console.log(records);
  return records;
};

const cleanEvents = function (entries) {
  let processed = [];
  function GetSortOrder(prop) {
    return function (a, b) {
      if (a[prop] > b[prop]) {
        return 1;
      } else if (a[prop] < b[prop]) {
        return -1;
      }
      return 0;
    };
  }

  for (const entry of entries) {
    const addressedTo = entry['From'];
    const department = entry['Department'];
    const venue = entry['Venue'];
    const days = entry['Day'];
    const event = entry['Event'];
    const timings = entry['Time'].toUpperCase();
    console.log(timings);
    const gender = entry['Gender'];

    processed.push({
      addressedTo,
      department,
      gender,
      venue,
      event,
      days,
      timings: timings,
    });
  }

  processed.sort(GetSortOrder('days'));

  const finalProcessed = {};
  for (const processedEvent of processed) {
    if (
      finalProcessed[processedEvent.department] == undefined ||
      finalProcessed[processedEvent.department] == null
    ) {
      finalProcessed[processedEvent.department] = [processedEvent];
    } else {
      finalProcessed[processedEvent.department].push(processedEvent);
    }
  }

  return finalProcessed;
};

const splitEvents = function (events) {
  const LIMIT = 8;
  const split = [];
  for (let index = 0; index < events.length; index += LIMIT) {
    split.push(events.slice(index, index + LIMIT));
  }

  return split;
};

const generateVenueLettersForDepartments = function (requests) {
  const documents = [];
  let serial = 6;
  for (const department in requests) {
    const events = splitEvents(requests[department]);
    // console.log(requests[department]);

    for (const chunk of events) {
      let fileName = `VL-${padSerial(
        serial
      )}-${department.trim()}.docx`.replaceAll(' ', '_');

      const doc = generateVenueLettersForDepartment(chunk, serial);
      serial++;
      documents.push({ fileName, doc });
    }
  }
  return documents;
};

const generateAndSave = async () => {
  const rawResponses = await processFile(CSV_FILE);
  const toBeDrafted = cleanEvents(rawResponses);
  const letters = generateVenueLettersForDepartments(toBeDrafted);

  for (const letter of letters) {
    const buffer = await Packer.toBuffer(letter.doc);

    // console.log(letter.fileName);
    writeFileSync(letter.fileName, buffer);
  }
};

generateAndSave();
