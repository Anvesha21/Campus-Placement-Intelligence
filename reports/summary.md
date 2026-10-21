# Campus Placement Intelligence: Summary

Author: Anveshaa Kesharwaani

> All data is synthetic (fictional). These numbers show how the pipeline works.
> They are not facts about any real college.

## Headline numbers

- Students: 1200
- Placement rate: 57.7%
- Share of offers from non-tech companies: 38.7%
- Average package, non-tech vs tech: 6.61 vs 11.15 LPA

## Placement rate by branch

| Branch | Students | Placed | Rate % | Avg package (LPA) |
|---|---|---|---|---|
| CSE | 329 | 197 | 59.9 | 10.58 |
| ECE | 295 | 173 | 58.6 | 9.48 |
| ME | 188 | 108 | 57.4 | 6.83 |
| IT | 260 | 146 | 56.2 | 10.66 |
| EE | 128 | 68 | 53.1 | 7.04 |

## Model

- Model used: **logistic_regression**
- Rule: the explainable logistic regression is kept unless another model beats it by more than 0.01 cross-validated ROC-AUC.
- Test ROC-AUC: 0.678
- Test accuracy: 0.66
- Test precision: 0.67, recall: 0.809

## Top 5 factors (logistic regression coefficients)

Positive means the factor raises placement odds. Negative means it lowers them.

| Feature | Coefficient |
|---|---|
| internships | 0.467 |
| cgpa | 0.444 |
| backlogs | -0.347 |
| coding_score | 0.286 |
| communication_score | 0.178 |
