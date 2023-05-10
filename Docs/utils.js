const numberToMoneyFormat = (number) => {
  let money = '';

  let num = parseInt(number);

  const lastThreeDigits = num % 1000;
  if (lastThreeDigits < 10) {
    money = '00' + lastThreeDigits;
  } else if (lastThreeDigits < 100) {
    money = '0' + lastThreeDigits;
  } else {
    money = '' + (num % 1000);
  }

  num = Math.floor(num / 1000);
  while (num > 0) {
    money = (num % 100) + ',' + money;
    num = Math.floor(num / 100);
  }
  return money;
};

const numberToWords = function (num) {
  const ones = [
    '',
    'One',
    'Two',
    'Three',
    'Four',
    'Five',
    'Six',
    'Seven',
    'Eight',
    'Nine',
    'Ten',
    'Eleven',
    'Twelve',
    'Thirteen',
    'Fourteen',
    'Fifteen',
    'Sixteen',
    'Seventeen',
    'Eighteen',
    'Nineteen',
  ];
  const tens = [
    '',
    '',
    'Twenty',
    'Thirty',
    'Forty',
    'Fifty',
    'Sixty',
    'Seventy',
    'Eighty',
    'Ninety',
  ];

  if (num == 0) {
    return 'Zero';
  }

  if (num < 0) {
    return 'Minus ' + numberToWords(Math.abs(num));
  }

  let words = '';

  if (Math.floor(num / 100000) > 0) {
    words += numberToWords(Math.floor(num / 100000)) + ' Lakh ';
    num %= 100000;
  }

  if (Math.floor(num / 1000) > 0) {
    words += numberToWords(Math.floor(num / 1000)) + ' Thousand ';
    num %= 1000;
  }

  if (Math.floor(num / 100) > 0) {
    words += numberToWords(Math.floor(num / 100)) + ' Hundred ';
    num %= 100;
  }

  if (num > 0) {
    if (words != '') {
      words += 'and ';
    }

    if (num < 20) {
      words += ones[num];
    } else {
      words += tens[Math.floor(num / 10)];
      if (num % 10 > 0) {
        words += ' ' + ones[num % 10];
      }
    }
  }

  return words.trim();
};

const numberSuffix = function (number) {
  if (number <= 10 || number >= 20) {
    const lastDigit = number % 10;

    if (lastDigit == 1) {
      return 'st';
    }
    if (lastDigit == 2) {
      return 'nd';
    }
    if (lastDigit == 3) {
      return 'rd';
    }
    return 'th';
  }

  return 'th';
};

const dateToWords = function (dateString) {
  const [month, day, year] = dateString.split('/');

  const months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ];

  const dayWord = day;
  const monthWord = months[parseInt(month) - 1];

  return `${dayWord}${numberSuffix(day)} ${monthWord}, ${year}`;
};

const getTodaysDate = function () {
  const today = new Date();
  const month = today.getMonth() + 1;
  const day = today.getDate();
  const year = today.getFullYear();
  const formattedDate = `${month}/${day}/${year}`;

  return formattedDate;
};

const padSerial = function (serial) {
  const num = parseInt(serial);
  if (num < 10) {
    return '00' + num;
  } else if (num < 100) {
    return '0' + num;
  }
  return num;
};

const generateAlias = function (companyFullName) {
  const wordsInName = companyFullName.split(' ');
  if (wordsInName.length <= 1) {
    return companyFullName;
  }

  const filtered = wordsInName.filter((word) => {
    return !word.match(
      /^inc\.?|pte\.?|ltd\.?|pvt\.?|incorporated|private|limited$/gi
    );
  });

  if (filtered.length > 1) {
    if (filtered.join(' ').length < 16) {
      return filtered.join(' ');
    }
    return (
      filtered
        .map((word) => {
          return word[0];
        })
        .join('.') + '.'
    );
  }
  return filtered.join(' ');
};

export {
  numberToMoneyFormat,
  numberToWords,
  numberSuffix,
  dateToWords,
  getTodaysDate,
  generateAlias,
  padSerial,
};
