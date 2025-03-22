The dashboard window should pop up with all the charts and filters!

## Screenshots
Here’s what the dashboard looks like:

![Anime Rating Dashboard](dashboard)

## What I Learned
- How to build a GUI with Tkinter and embed Matplotlib charts in it.
- Working with large datasets using Pandas (I had to sample `rating.csv` because it’s huge!).
- Creating different types of visualizations (bar charts, pie charts, histograms, scatter plots) with Seaborn.
- Adding interactivity with a genre filter dropdown.

## Future Ideas
- Add a search bar to find specific anime by name.
- Include more charts, like a scatter plot for episodes vs. rating.
- Maybe add tooltips to the charts so you can hover and see more details.

## About the Data
The datasets are from Kaggle:
- `anime.csv`: Contains anime details like title, genre, type, episodes, official rating, and number of members.
- `rating.csv`: Contains user ratings for anime (user_id, anime_id, rating).

**Note**: The `rating.csv` file is large, so I sampled 1 million rows in the code to make it run faster. You can adjust the `nrows` parameter in `main.py` if you want to use more data.

## License
This project is licensed under the MIT License - feel free to use it however you like!

## Contact
If you have any questions or suggestions, feel free to reach out! You can find me on [GitHub](https://github.com/Adiii18) or [LinkedIn](https://www.linkedin.com/in/aditya-pratap-49538a250/).

Thanks for checking out my project! 😊
