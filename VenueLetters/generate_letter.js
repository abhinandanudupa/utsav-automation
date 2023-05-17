import docx from 'docx';

import { readFileSync } from 'node:fs';
const {
  Document,
  Paragraph,
  Header,
  TextRun,
  ImageRun,
  convertInchesToTwip,
  AlignmentType,
  WidthType,
  UnderlineType,
  HeadingLevel,
  Table,
  TableRow,
  TableCell,
} = docx;

// import { getDeliverablesFromPackage } from './sponsorship_packages.js';
import {
  padSerial,
  generateAlias,
  numberToMoneyFormat,
  numberToWords,
  dateToWords,
  getTodaysDate,
} from './utils.js';

const generateVenueLettersForDepartment = (department, serial) => {
  // console.log(department);
  const documentStructure = [];
  const allotment = department[0];

  const header = new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [
      new ImageRun({
        data: readFileSync('./logo.png'),
        transformation: {
          width: 40,
          height: 40,
        },
      }),
      new TextRun({
        text: 'B. M. S. COLLEGE OF ENGINEERING, BENGALURU-19',
        size: 32,
        break: 1,
      }),
      new TextRun({ text: 'UTSAV 2023', break: 1, size: 32 }),
    ],
    break: 2,
  });
  documentStructure.push(header);

  const serialLabel = new Paragraph({
    children: [
      new TextRun({
        text: `BMS/UTSAV/2023/042/${padSerial(serial)}`,
        break: 2,
      }),
    ],
    alignment: AlignmentType.LEFT,
  });
  documentStructure.push(serialLabel);

  const addressLines = [
    new TextRun({ text: `${allotment.addressedTo.trim()}`, break: 3 }),
    new TextRun({ text: `${allotment.department}`, break: 1 }),
  ];

  if (allotment.department.trim() !== 'BMS College of Engineering') {
    addressLines.push(new TextRun({ text: 'BMSCE', break: 1 }));
  }

  const address = new Paragraph({
    children: addressLines,
  });
  documentStructure.push(address);

  const todaysDate = new Paragraph({
    children: [new TextRun({ text: '16th May 2023', break: 1 })],
  });
  documentStructure.push(todaysDate);

  const salutation = new Paragraph({
    children: [
      new TextRun({
        text: `Respected ${allotment.gender === 'M' ? 'Sir' : "Ma'am"},`,
        break: 1,
      }),
    ],
  });
  documentStructure.push(salutation);

  const subject = new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [
      new TextRun({
        text: 'Subject: Permission to use the below mentioned venues',
        break: 1,
      }),
    ],
  });
  documentStructure.push(subject);

  const body = new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    children: [
      new TextRun({
        text: 'With respect to the above subject, we humbly request your permission to utilize the following venue(s) on the mentioned dates, to conduct the events of UTSAV 2023. We shall require the venue(s) for the below mentioned timings. Henceforth, 26th, 27th and 28th of May 2023 shall be referred to as Day 1, 2 and 3 respectively. ',
        break: 1,
      }),
    ],
  });
  documentStructure.push(body);

  documentStructure.push(
    new Paragraph({
      children: [new TextRun({ text: '', break: 1 })],
    })
  );

  let events = [];
  events.push(
    new TableRow({
      children: [
        new TableCell({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [
                new TextRun({
                  text: 'Venue',
                  alignment: AlignmentType.CENTER,
                  bold: true,
                }),
              ],
            }),
          ],
        }),
        new TableCell({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [
                new TextRun({
                  text: 'Events',
                  alignment: AlignmentType.CENTER,
                  bold: true,
                }),
              ],
            }),
          ],
        }),
        new TableCell({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [
                new TextRun({
                  text: 'Days',

                  bold: true,
                }),
              ],
            }),
          ],
        }),
        new TableCell({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [
                new TextRun({
                  text: 'Timings',

                  bold: true,
                }),
              ],
            }),
          ],
        }),
      ],
      cantSplit: true,
    })
  );

  const required = department.map((allotment) => {
    // console.log(allotment);
    return new TableRow({
      children: [
        new TableCell({
          children: [
            new Paragraph({
              text: allotment.venue.trim(),
              alignment: AlignmentType.CENTER,
            }),
          ],
        }),
        new TableCell({
          children: [
            new Paragraph({
              text: allotment.event.trim(),
              alignment: AlignmentType.CENTER,
            }),
          ],
        }),
        new TableCell({
          children: [
            new Paragraph({
              text: allotment.days,
              alignment: AlignmentType.CENTER,
            }),
          ],
        }),
        new TableCell({
          children: [
            new Paragraph({
              text: allotment.timings,
              alignment: AlignmentType.CENTER,
            }),
          ],
        }),
      ],
      cantSplit: true,
    });
  });
  events = events.concat(required);

  const table = new Table({
    rows: events,
    width: {
      size: '100%',
      type: WidthType.PERCENTAGE,
    },
  });
  documentStructure.push(table);

  const thanks = new Paragraph({
    children: [new TextRun({ text: 'Thank you in advance.', break: 3 })],
  });
  documentStructure.push(thanks);

  const signLabels = new Paragraph({
    children: [
      new TextRun({
        text: 'Student Coordinator\t\t\t\tOrganising Secretary',
        break: 3,
      }),
    ],
  });
  documentStructure.push(signLabels);

  const utsav = new Paragraph({
    text: 'UTSAV 2023\t\t\t\t\tUTSAV 2023',
  });
  documentStructure.push(utsav);

  // Student Coordinator
  // Organising Secretary
  // UTSAV 2023
  // UTSAV 2023

  return new Document({
    creator: 'UTSAV 2023',
    description: 'Venue Letters for the department.',
    title: 'Venue Letters',
    compatibility: {
      version: 15,
      doNotExpandShiftReturn: true,
      growAutofit: true,
    },
    sections: [
      {
        default: new Header({
          // The standard default header on every page or header on odd pages when the 'Different Odd & Even Pages' option is activated
          children: [header],
        }),
        children: documentStructure,
      },
    ],
  });
};

export { generateVenueLettersForDepartment };
