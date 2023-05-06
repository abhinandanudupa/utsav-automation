import { parse } from 'csv-parse';
import { createReadStream, writeFileSync } from 'node:fs';

import docx from 'docx';
const { Packer } = docx;

import { generateMoUForCompany } from './generate_mou.js';
import { padSerial } from './utils.js';

const CSV_FILE = './responses.csv';

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
  return records;
};

const cleanResponses = function (responses) {
  const processed = [];
  for (const response of responses) {
    const companyName = response['OFFICIAL Name of the sponsor'];
    const clubName = response['Club Name'];
    const companyEmail = response['Email ID of the Company'];
    const chosenPackage = response['Package chosen by the company'];
    const otherDeliverables = response['Additional/Customised Deliverables'];
    const sponsoredAmount = response['Sponsored amount'];
    const expectedPaymentDate = response['Expected payment date'];
    const nonMonetaryDeliverables = response['Non monetary benefits'];
    const alreadyDrafted = response['MoU drafted?'];
    const serial = response['MoU Serial'];

    processed.push({
      companyName,
      clubName,
      companyEmail,
      chosenPackage,
      otherDeliverables,
      sponsoredAmount,
      expectedPaymentDate,
      nonMonetaryDeliverables,
      alreadyDrafted,
      serial,
    });
  }

  return processed;
};

const generateMoUsForCompanies = function (companies) {
  const documents = [];
  for (const companyObj of companies) {
    const fileName = `${padSerial(companyObj.serial)}-MoU-${
      companyObj.clubName
    }-${companyObj.companyName}.docx`.replaceAll(' ', '_');
    const doc = generateMoUForCompany(companyObj);
    documents.push({ fileName, doc });
  }
  return documents;
};

const generateAndSave = async () => {
  const rawResponses = await processFile(CSV_FILE);
  const toBeDrafted = cleanResponses(rawResponses).filter((response) => {
    return response.alreadyDrafted === 'FALSE';
  });
  const mous = generateMoUsForCompanies(toBeDrafted);

  for (const mou of mous) {
    const buffer = await Packer.toBuffer(mou.doc);
    writeFileSync(mou.fileName, buffer);
  }
};

generateAndSave();
