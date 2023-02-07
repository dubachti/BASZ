# Best Area for Students to live in Zurich (BASZ)

This project tries to determine the best area for students to live in Zurich based on available flats listed on [immoscout24.ch](https://www.immoscout24.ch)
using a defined Score metric which reflects how great a flat is and the price itself.

*Note that this just an exercise on how to aquire, store and evaluate web data using Python and BigQuery. The significance of the score function is also up for debate.*

# Overview
This project extracts and preprocesses the provided data on the website (address, price, floor area, number of rooms and price) and pushes it to Google BigQuery.
As it is important for students to get to university quickly (in order to sleep longer in the morning), the cycling time and cycling distance attributes are 
calculated using the Google Directions API. (The destination point is ETHZ Zentrum.)

Next the data is queried where the Score is calculated for each instance. The Score metric is given by:

Score := $(\frac{{Num. Rooms}}{{Floor Area}})^{0.5} + (\frac{1}{{Cycle Distance} + {Cycle Time}})^{0.5}$

Finally the flats, clustered by zip code, are plotted on the Score and price axis's.

# Output

Considering the results on 03.02.2023, we see that the best but most expensive area to live is zip code 8008 (Seefeld) (as expected). 
However, due to the central importance of the price, it is therefore more recommended to move to code 8003 (Wiedikon etc.).

![alt text](https://github.com/dubachti/BASZ/blob//master/cluster.png?raw=true)
