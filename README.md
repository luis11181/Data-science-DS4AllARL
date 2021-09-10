
# DS4AllPOSITIVA

# Machine learning program to predict clients churn(retiros)🖥️   
####  python/ dash/ plotly/ postgres..
![positiva](https://user-images.githubusercontent.com/80784724/131435030-7e8573c4-6271-4599-b8a9-3583a707a3aa.png)

## 🎨 Screenshots

![ezgif com-gif-maker](https://user-images.githubusercontent.com/80784724/131929043-1426553d-f2f6-4089-b233-0f3f80e85b90.gif)



## :page_facing_up: Description 


📢 

## 💾  Data
This project aims to avoid customer churn by analyzing previous data, understanding the reasons, and predicting future dropout cases. leading to a more efficient company that can focus it's resources on the right places.
Based on some basic payment records for each company we did generate some new and more meaningful tables that were good to run some machine learning algorithms to predict dropouts.



All data transformations was done with postgres functions.

## data exploration and description

This page section contains interactive graphs over time and maps, the displayed information can be changed, grouped and filtered by categories and years, giving a deep understanding of each metric. 
![positiva2](https://user-images.githubusercontent.com/80784724/131430720-84222f8f-bf77-4b1c-baed-e623cccd7773.png)

## reasons for withdrawal/ voice of the client

in this page section there are graphs that summarize the texts submmited by the clients that leave the company, explaining their reasons, it is also posible to filter and see all the withdrawal reasons, by specific words, categories etc... Giving a good look at the main reasons and posible actions for improvement.


![positiva3](https://user-images.githubusercontent.com/80784724/131430719-bcf81e3a-81a8-46a9-b318-e5230400d96e.png)

## Machine learning forecast

in this section we used the new created data to predict which clients were more prone to leave the company, giving a withdrawal 
probability that can be filter by categories.


Confution matrix showing an average accuracy rate of almost 90%! accomplished with a logistic regression.

![cm_LR](https://user-images.githubusercontent.com/80784724/131927515-ca7deda7-0060-47fa-9748-d09cae2daade.png)

![forecast](https://user-images.githubusercontent.com/80784724/131927474-b6c39b23-5cd5-4606-981f-643cd753c7ac.png)


All the tools provided by the app are a great step into the inicial goal of the project "avoid customer churn", and with this data and the apropied measurements it can be accomplished.

## 📁 overall structure
```
└── project
    ├── __trash__
    ├── assets
    │    ├── icons.svg
    │    ├── readme.gif
    │    ├── images
    │    └── styles.css
    │    
    ├── analysis
    │    ├── description page
    │    ├── main menu page
    │    └── reasons page
    │
    ├── forecast
    │    ├── model_eval
    │    ├── model_selection
    │    ├── models.pkl
    |    ├── models.output
    │    └── scaler.pkl
    ├── p_acquisition
    │    ├── __init__.py
    │    └── m_acquisition.py
    ├── p_graphic
    │    ├── __init__.py
    │    └── m_graphic.py
    ├── others
    │    └── 
    ├── .gitignore
    ├──  __init__.py
    ├── app.py
    ├── data.py
    ├── index.py
    ├── run_production.py
    ├── README.md
    └── requeriments.txt  

```

