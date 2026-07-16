const expenseInputs = document.querySelectorAll("[data-expense]");

const purchasePriceInput = document.querySelector("#purchasePrice");
const depreciationRateInput = document.querySelector("#depreciationRate");
const monthlyDepreciationElement = document.querySelector("#monthlyDepreciation");

const monthlyTotalElement = document.querySelector("#monthlyTotal");
const weeklyTotalElement = document.querySelector("#weeklyTotal");
const yearlyTotalElement = document.querySelector("#yearlyTotal");

const currencyFormatter = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0
});

function getPositiveNumber(input) {
  const value = Number(input.value);
  return Number.isFinite(value) && value > 0 ? value : 0;
}

function calculateTotals() {
  let monthlyTotal = 0;

  expenseInputs.forEach((input) => {
    monthlyTotal += getPositiveNumber(input);
  });

  const purchasePrice = getPositiveNumber(purchasePriceInput);
  const depreciationRate = getPositiveNumber(depreciationRateInput);
  const monthlyDepreciation = purchasePrice * (depreciationRate / 100) / 12;

  monthlyTotal += monthlyDepreciation;

  const weeklyTotal = monthlyTotal * 12 / 52;
  const yearlyTotal = monthlyTotal * 12;

  monthlyDepreciationElement.textContent = `${currencyFormatter.format(monthlyDepreciation)} в месяц`;
  monthlyTotalElement.textContent = currencyFormatter.format(monthlyTotal);
  weeklyTotalElement.textContent = currencyFormatter.format(weeklyTotal);
  yearlyTotalElement.textContent = currencyFormatter.format(yearlyTotal);
}

const calculatorInputs = document.querySelectorAll("input");

calculatorInputs.forEach((input) => {
  input.addEventListener("input", calculateTotals);
});

calculateTotals();
