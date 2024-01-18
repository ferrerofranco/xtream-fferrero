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
  
Being limited by lack of architecture and time, in this case I'll work on a flow that is more like   
- Load data -> process data -> train model -> predict -> check prediction  
I'll simulate having a cloud storage (like aws S3) with a file for each year of data. The idea is that each year a new file would be deposited, and we would trigger a retrain of our model with the most up to date data and create a prediction on the following year. In our case this triggering will be manual with a specified target date, so we can test and run however many times we want.  
We'll use a parameter `target_year`, that will indicate up to when we should collect data. The last year will be kept from the training set to let us validate and generate our metrics, since we'll do the forecast for it. 
  
Some boundaries I've set to delimit the scope of the project due to necessity:  

- There will be no comparison with the older models
- As mentioned, each time we trigger the process, there will be a training and a subsequent forecast.
- Model hyperparameters will stay fixed, with the exception of Epochs that can be altered in the configuration file. This is for faster testing, each epoch takes about 5 min on my computer, you milage may vary. 
- Alerts will be logged on a table, you'll have to use the "access database" notebook to look at it easily. 
- I will assume this is a batch processing process and there is no need for APIs, asynchronicity or such achitecture. 

The overall architecture that I will use is as follows:  
- main -> extractor/enricher/trainer -> controller -> DAOs  
  
The main would be called likely through SSH by an orchestrator. Main module then asks the extractor, enricher and trainer to do what they were created to do. These will call on the data controller whenever they need to consume or write any type of data. The data controller will have minimal coding and its job will mostly be to know who to ask for each piece of data, be it to retrieve it or save it. The DAOs (Data Access Objects) will know how to interact with each information source, this could be different databases (in which case there would be one for each if the code differs much), APIs, cloud storage, etc.  
This way we try to abstract as much as possible each layer from the next, so it is easier to maintain. When we need to say, now get information from MySQL in ServerA that we previously got from Redshift in serverB, we can create a new DAO (or modify an existing one if we had one) and point the data controller to that new DAO, and it remains transparent for the rest of the program.
