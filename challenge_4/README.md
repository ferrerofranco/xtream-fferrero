# Challenge 4
Challenge 4 reads:  
> *Choose one of your sparkling models and get it ready for the big leagues.*  
> *Develop an **end-to-end pipeline for training and evaluating your model** on 2020 and 2021 data.*  
> *Luca, the new CTO at Zap and a self-confessed nerd, demands code that's as clean and structured as it is maintainable.*  
> *Impress him!*  
  
What I understand as an end-to-end ML pipeline is something that can have these two flows at a minimum:
1. Load data -> process data -> train model -> save model
2. Load new data -> process data -> load model -> predict using new data
  
These two should be able to run on command through a scheduler like Airflow. There can also be modifications to these flows, for example, on flow 1 we could add steps to compare performance metrics to previous models to decide if the new model will be the new production model to be used. Also when we say "save model" we could also be saying "deploy model", depending on the architecture we are using.  
Furthermore, the pipeline can be more or less complex, adding data checks for things like data type, missing values, number of expected features, or further still, checking on feature distribution with threshold alerts to let us know that something is wrong or might have changed in the reality of our data that will either make our trained model do poorly, or trigger a re-training. We can have similar checks on our predictions.  We can, and should, also have some type of dashboard that gives us metrics on our model's performance on important metrics (and some alerts would be preferable as well).  
  
Being limited by lack of architecture in this case, I'll simulate having a cloud storage (like aws S3) with a file for each year of data. The idea is that each year a new file would be deposited, and we would trigger a new full-year prediction. In our case this triggering will be manual with a specified target date, so we can test and run however many times we want.  
We'll use a parameter `target_year`, in case of training, it will be the last year to be included in the training process (previous to doing so, we'll train once without it and use it to create our metrics). In case of forecast it will be the year to be forecasted with the trained model. 
  
Some boundaries I've set to delimit the scope of the project:  

- If the new model performs better with the validation data, it will be taken as a new productive model.  
- The retraining will not be automatic, and the hyperparameters will stay fixed. 
- Alerts will be logged on a table, we'll have a flow to print them on screen. 
- I will assume this is a batch processing process and there is no need for APIs, asynchronicity or such achitecture. 
- There will be no validation on whether the forecast year was included in the training process.