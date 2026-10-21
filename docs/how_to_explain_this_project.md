# How to explain this project

Author: Anveshaa Kesharwaani

## The 60-second version

"I built a placement analytics project on a synthetic dataset of 1,200 students. I stored it in a SQL database and wrote views to answer questions like which branches place best and how much non-tech companies contribute. I trained a model to estimate each student's placement chance and compared two models. I exported the results and built dashboards in Power BI and Tableau. The data is fictional, so the numbers show the method, not facts about a real college."

## Be accurate about what is yours

Interviewers ask follow-up questions. Say only what you can back up. The Python code in this repository was written with AI assistance. Before an interview, run the pipeline yourself, read `docs/sql_views_explained.md`, build the Power BI dashboard yourself using `docs/powerbi_guide.md`, and be ready to explain one SQL view and one DAX measure in your own words.

## Likely questions

**Why is the data synthetic?**
Real placement records contain personal information and are not public. I generated fictional data with a made-up rule. The patterns in it exist because I put them there, so they are not findings about real students.

**Why logistic regression?**
It is easy to explain: each factor has a coefficient that shows whether it raises or lowers placement odds. Random forest scored 0.695 against 0.691 for logistic regression in cross-validation. That gap is too small to justify a model I cannot explain as easily.

**What does a ROC-AUC of 0.68 mean?**
ROC-AUC is 0.5 for guessing and 1.0 for a perfect model. At 0.68, the model ranks placed students above unplaced ones somewhat better than chance. It is modest, so one student's estimate is a rough guide only.

**What does "out-of-fold" mean?**
Each student's score comes from a model that never saw that student during training. Scoring students with a model trained on them would flatter the results.

**How do you know the dashboard numbers are right?**
I reconcile them against SQL. The placement rate on the dashboard should equal the rate from `SELECT SUM(placed) * 100.0 / COUNT(*) FROM students`, which is 57.7%.

**What is the difference between a DAX measure and a calculated column?**
A calculated column is computed once per row when data refreshes. A measure is computed on demand and changes with filters and slicers. Placement Rate has to be a measure so it recalculates for each branch or band.

**What is the difference between a view and a table?**
A table stores data. A view stores a query and shows the current data each time.

**What would you do with real data?**
Anonymise it, check for missing values, and test whether the model treats different groups differently before using it for anything. I would also recalibrate the thresholds.

**What are the limits?**
The data is fictional, the model is modest, and the advice is a comparison with placed students, not proof that a change causes an offer.
