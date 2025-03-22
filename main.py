import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import textwrap  # for wrapping long anime names

# Hey, this is my Anime Rating Dashboard project! I built it to analyze anime data and make cool charts.
# It uses Tkinter for the GUI and Seaborn for the plots. Let's get started!

class animeDashboard:  # I like camelCase for class names, makes it feel more personal
    def __init__(self, root):
        self.root = root
        self.root.title("Anime Rating Dashboard")
        self.root.configure(bg="#2C2F33")  # dark background looks sleek
        self.animeData = None  # to store anime.csv data
        self.ratingsData = None  # to store rating.csv data
        self.mergedData = None  # merged dataset for analysis

        # Load the data when the app starts
        self.loadData()

        # Set up the GUI with all the charts and stuff
        self.setup_gui()

    def loadData(self):
        # I need to load the CSV files from the 'csv' folder
        baseDir = os.path.dirname(__file__)
        csvFolder = os.path.join(baseDir, "csv")  # path to csv folder
        animeFile = os.path.join(csvFolder, "anime.csv")
        ratings_file = os.path.join(csvFolder, "rating.csv")  # I used underscore here, oops

        # Load anime.csv - this has all the anime details
        if os.path.exists(animeFile):
            self.animeData = pd.read_csv(animeFile)
            self.animeData.dropna(subset=['rating'], inplace=True)  # drop rows with missing ratings
            self.animeData['episodes'] = pd.to_numeric(self.animeData['episodes'], errors='coerce')  # handle 'Unknown' episodes
        else:
            raise FileNotFoundError("Oops, anime.csv is missing in the 'csv' folder!")

        # Load rating.csv - this has user ratings, it's a big file so I sample it
        if os.path.exists(ratings_file):
            self.ratingsData = pd.read_csv(ratings_file, usecols=['user_id', 'anime_id', 'rating'], nrows=1000000)
            self.ratingsData = self.ratingsData[self.ratingsData['rating'] != -1]  # ignore -1 ratings
        else:
            raise FileNotFoundError("rating.csv not found in the 'csv' folder! :(")

        # Merge the datasets to get user ratings for each anime
        userAvgRatings = self.ratingsData.groupby('anime_id')['rating'].mean().reset_index()
        self.mergedData = pd.merge(self.animeData, userAvgRatings, on='anime_id', how='inner', 
                                  suffixes=('_official', '_user'))

    def setup_gui(self):
        # Add a title to the dashboard
        titleLabel = tk.Label(self.root, text="Anime Rating Dashboard", font=("Helvetica", 20, "bold"), 
                             fg="#FFFFFF", bg="#2C2F33", pady=10, padx=20, 
                             highlightbackground="#FFD700", highlightthickness=2)
        titleLabel.pack(pady=15)

        # Create a scrollable canvas for the main frame
        canvas = tk.Canvas(self.root, bg="#2C2F33")
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollableFrame = tk.Frame(canvas, bg="#2C2F33")

        scrollableFrame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollableFrame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")

        # First row: Top genres, anime type distribution, and top by episode count
        row1Frame = tk.Frame(scrollableFrame, bg="#2C2F33")
        row1Frame.pack(fill="x", expand=True, pady=(0, 15))  # Added padding between rows

        # Summary frame - bar chart for top genres
        summaryFrame = tk.Frame(row1Frame, bg="#2C2F33", bd=2, relief="groove", highlightbackground="#FFD700")
        summaryFrame.pack(side=tk.LEFT, padx=10, pady=10, fill="both", expand=True)
        self.showSummary(summaryFrame)

        # Pie chart for anime types (TV, Movie, etc.)
        typeFrame = tk.Frame(row1Frame, bg="#2C2F33", bd=2, relief="groove", highlightbackground="#FFD700")
        typeFrame.pack(side=tk.LEFT, padx=10, pady=10, fill="both", expand=True)
        self.showTypeDistribution(typeFrame)

        # New chart: Top 5 anime by episode count
        episodeFrame = tk.Frame(row1Frame, bg="#2C2F33", bd=2, relief="groove", highlightbackground="#FFD700")
        episodeFrame.pack(side=tk.LEFT, padx=10, pady=10, fill="both", expand=True)
        self.showTopEpisodes(episodeFrame)

        # Second row: Top 5 official and top 5 user ratings
        row2Frame = tk.Frame(scrollableFrame, bg="#2C2F33")
        row2Frame.pack(fill="x", expand=True, pady=(0, 15))

        # Top 5 by official rating - using a bar chart
        officialFrame = tk.Frame(row2Frame, bg="#2C2F33", bd=2, relief="groove", highlightbackground="#FFD700")
        officialFrame.pack(side=tk.LEFT, padx=10, pady=10, fill="both", expand=True)
        self.showTopOfficial(officialFrame)

        # Top 5 by user rating - also a bar chart
        userFrame = tk.Frame(row2Frame, bg="#2C2F33", bd=2, relief="groove", highlightbackground="#FFD700")
        userFrame.pack(side=tk.LEFT, padx=10, pady=10, fill="both", expand=True)
        self.showTopUser(userFrame)

        # Genre filter dropdown
        filterFrame = tk.Frame(scrollableFrame, bg="#2C2F33", bd=2, relief="groove", highlightbackground="#FFD700")
        filterFrame.pack(pady=10, fill="x")
        self.setupGenreFilter(filterFrame)

        # Frame for the genre chart
        self.genreStatsFrame = tk.Frame(scrollableFrame, bg="#2C2F33", bd=2, relief="groove", highlightbackground="#FFD700")
        self.genreStatsFrame.pack(pady=10, fill="both", expand=True)

        # Notebook for the bigger plots
        notebook = ttk.Notebook(scrollableFrame)
        notebook.pack(pady=10, expand=True, fill="both")

        # Frames for the tabs
        self.topFrame = ttk.Frame(notebook)
        self.distFrame = ttk.Frame(notebook)
        self.compFrame = ttk.Frame(notebook)
        
        notebook.add(self.topFrame, text="Top Anime")
        notebook.add(self.distFrame, text="Rating Distribution")
        notebook.add(self.compFrame, text="Rating Comparison")

        # Plot the charts in the tabs
        self.plotTopAnime(self.topFrame)
        self.plotRatingDist(self.distFrame)
        self.plotRatingComparison(self.compFrame)

    def showSummary(self, frame):
        # Show top 5 genres by number of anime
        genreCounts = {}
        for genres in self.mergedData['genre'].dropna():
            for genre in genres.split(","):
                genre = genre.strip()
                genreCounts[genre] = genreCounts.get(genre, 0) + 1
        topGenres = pd.Series(genreCounts).nlargest(5)

        # Wrap long genre names
        wrappedGenres = [textwrap.fill(genre, 10) for genre in topGenres.index]
        topGenres.index = wrappedGenres

        fig, ax = plt.subplots(figsize=(6, 4), facecolor="#2C2F33")  # Adjusted size
        ax.set_facecolor("#3A3D41")
        sns.barplot(x=topGenres.values, hue=topGenres.index, y=topGenres.index, ax=ax, palette='YlOrBr', legend=False)
        plt.title('Top 5 Genres by Anime Count', color="#FFFFFF", fontsize=14, fontweight='bold')
        plt.xlabel('Number of Anime', color="#FFFFFF", fontsize=10)
        plt.ylabel('Genre', color="#FFFFFF", fontsize=10)
        plt.xticks(color="#FFFFFF", fontsize=8)
        plt.yticks(color="#FFFFFF", fontsize=9)
        ax.grid(True, color="#555555", linestyle="--", alpha=0.7)
        plt.tight_layout()
        self.showPlot(fig, frame)

    def showTypeDistribution(self, frame):
        # Pie chart for anime types
        typeCounts = self.mergedData['type'].value_counts()
        
        fig, ax = plt.subplots(figsize=(6, 4), facecolor="#2C2F33")  # Increased size to match other charts
        ax.set_facecolor("#3A3D41")
        plt.pie(typeCounts, labels=typeCounts.index, autopct='%1.1f%%', 
                colors=sns.color_palette("Set2"), textprops={'color': "#FFFFFF", 'fontsize': 10},
                shadow=True, labeldistance=1.1)  # Increased font size and padding
        plt.title('Anime Type Distribution', color="#FFFFFF", fontsize=14, fontweight='bold')
        plt.tight_layout()
        self.showPlot(fig, frame)

    def showTopEpisodes(self, frame):
        # New chart: Top 5 anime by episode count
        topEpisodes = self.mergedData.nlargest(5, 'episodes')[['name', 'episodes']].dropna()
        
        # Wrap long anime names
        wrappedNames = [textwrap.fill(name, 15) for name in topEpisodes['name']]
        topEpisodes['name'] = wrappedNames

        fig, ax = plt.subplots(figsize=(6, 4), facecolor="#2C2F33")  # Same size as other charts
        ax.set_facecolor("#3A3D41")
        sns.barplot(x='episodes', hue='name', y='name', data=topEpisodes, ax=ax, palette='Greens_r', legend=False)
        plt.title('Top 5 Anime by Episode Count', color="#FFFFFF", fontsize=14, fontweight='bold')
        plt.xlabel('Episode Count', color="#FFFFFF", fontsize=10)
        plt.ylabel('Anime', color="#FFFFFF", fontsize=10)
        plt.xticks(color="#FFFFFF", fontsize=8)
        plt.yticks(color="#FFFFFF", fontsize=9)
        ax.grid(True, color="#555555", linestyle="--", alpha=0.7)
        plt.tight_layout()
        self.showPlot(fig, frame)

    def showTopOfficial(self, frame):
        # Top 5 anime by official rating as a bar chart
        topOfficial = self.mergedData.nlargest(5, 'rating_official')[['name', 'rating_official']]
        
        # Wrap long anime names
        wrappedNames = [textwrap.fill(name, 15) for name in topOfficial['name']]
        topOfficial['name'] = wrappedNames

        fig, ax = plt.subplots(figsize=(6, 4), facecolor="#2C2F33")  # Adjusted size
        ax.set_facecolor("#3A3D41")
        sns.barplot(x='rating_official', hue='name', y='name', data=topOfficial, ax=ax, palette='Blues_r', legend=False)
        plt.title('Top 5 by Official Rating', color="#FFFFFF", fontsize=14, fontweight='bold')
        plt.xlabel('Rating', color="#FFFFFF", fontsize=10)
        plt.ylabel('Anime', color="#FFFFFF", fontsize=10)
        plt.xticks(color="#FFFFFF", fontsize=8)
        plt.yticks(color="#FFFFFF", fontsize=9)
        ax.grid(True, color="#555555", linestyle="--", alpha=0.7)
        plt.tight_layout()
        self.showPlot(fig, frame)

    def showTopUser(self, frame):
        # Top 5 anime by user rating as a bar chart
        topUser = self.mergedData.nlargest(5, 'rating_user')[['name', 'rating_user']]
        
        # Wrap long anime names
        wrappedNames = [textwrap.fill(name, 15) for name in topUser['name']]
        topUser['name'] = wrappedNames

        fig, ax = plt.subplots(figsize=(6, 4), facecolor="#2C2F33")  # Adjusted size
        ax.set_facecolor("#3A3D41")
        sns.barplot(x='rating_user', hue='name', y='name', data=topUser, ax=ax, palette='Reds_r', legend=False)
        plt.title('Top 5 by User Rating', color="#FFFFFF", fontsize=14, fontweight='bold')
        plt.xlabel('Rating', color="#FFFFFF", fontsize=10)
        plt.ylabel('Anime', color="#FFFFFF", fontsize=10)
        plt.xticks(color="#FFFFFF", fontsize=8)
        plt.yticks(color="#FFFFFF", fontsize=9)
        ax.grid(True, color="#555555", linestyle="--", alpha=0.7)
        plt.tight_layout()
        self.showPlot(fig, frame)

    def setupGenreFilter(self, frame):
        # Dropdown to filter anime by genre
        tk.Label(frame, text="Filter by Genre:", font=("Helvetica", 12), fg="#FFFFFF", bg="#2C2F33").pack(side=tk.LEFT, padx=5)
        
        allGenres = set()
        for genres in self.mergedData['genre'].dropna():
            for genre in genres.split(","):
                allGenres.add(genre.strip())
        self.genresList = sorted(list(allGenres))

        self.genreVar = tk.StringVar(value="All")
        genreMenu = ttk.Combobox(frame, textvariable=self.genreVar, values=["All"] + self.genresList, state="readonly")
        genreMenu.pack(side=tk.LEFT, padx=5)
        genreMenu.bind("<<ComboboxSelected>>", self.updateGenreStats)

    def updateGenreStats(self, event=None):
        # Clear previous chart
        for widget in self.genreStatsFrame.winfo_children():
            widget.destroy()

        genre = self.genreVar.get()
        if genre == "All":
            filteredDf = self.mergedData
        else:
            filteredDf = self.mergedData[self.mergedData['genre'].str.contains(genre, na=False)]

        if not filteredDf.empty:
            topGenre = filteredDf.nlargest(5, 'rating_user')[['name', 'rating_user']]
            
            # Wrap long anime names
            wrappedNames = [textwrap.fill(name, 20) for name in topGenre['name']]
            topGenre['name'] = wrappedNames

            # Create a bar chart for the top 5 genre anime
            fig, ax = plt.subplots(figsize=(12, 6), facecolor="#2C2F33")  # Increased height for wrapped names
            ax.set_facecolor("#3A3D41")
            sns.barplot(x='rating_user', hue='name', y='name', data=topGenre, ax=ax, palette='cool', legend=False)
            plt.title(f'Top 5 {genre} Anime (User Ratings)', color="#FFFFFF", fontsize=16, fontweight='bold')
            plt.xlabel('User Rating', color="#FFFFFF", fontsize=12)
            plt.ylabel('Anime', color="#FFFFFF", fontsize=12)
            plt.xticks(color="#FFFFFF", fontsize=10)
            plt.yticks(color="#FFFFFF", fontsize=9)
            ax.grid(True, color="#555555", linestyle="--", alpha=0.7)
            plt.tight_layout()
            self.showPlot(fig, self.genreStatsFrame)
        else:
            tk.Label(self.genreStatsFrame, text=f"No anime found for genre: {genre}", 
                    font=("Helvetica", 12), fg="#FF5555", bg="#2C2F33").pack(pady=5)

    def plotTopAnime(self, frame):
        # Plot the top 10 anime with official vs user ratings
        fig, ax = plt.subplots(figsize=(12, 6), facecolor="#2C2F33")  # Adjusted size
        ax.set_facecolor("#3A3D41")
        topDf = self.mergedData.nlargest(10, 'rating_official')
        
        # Wrap long names so they fit horizontally
        wrappedNames = [textwrap.fill(name, 15) for name in topDf['name']]
        topDf['wrapped_name'] = wrappedNames
        
        sns.barplot(x='wrapped_name', y='rating_official', data=topDf, ax=ax, label='Official', color='#00CED1')
        sns.barplot(x='wrapped_name', y='rating_user', data=topDf, ax=ax, alpha=0.6, label='User', color='#FF4500')
        plt.title('Top 10 Anime: Official vs User Ratings', color="#FFFFFF", fontsize=16, fontweight='bold', pad=20)
        
        plt.xticks(rotation=0, ha='center', color="#FFFFFF", fontsize=9, fontweight='bold')
        ax.set_xlabel("Anime Name", color="#FFFFFF", fontsize=12)
        ax.set_ylabel("Rating", color="#FFFFFF", fontsize=12)
        ax.tick_params(axis='y', colors="#FFFFFF")
        
        for label in ax.get_xticklabels():
            label.set_bbox(dict(facecolor='#2C2F33', edgecolor='none', alpha=0.8, pad=2))
        
        plt.legend(facecolor="#2C2F33", edgecolor="#FFFFFF", labelcolor="#FFFFFF")
        ax.grid(True, color="#555555", linestyle="--", alpha=0.7)
        plt.tight_layout()
        self.showPlot(fig, frame)

    def plotRatingDist(self, frame):
        # Histogram for user rating distribution
        fig, ax = plt.subplots(figsize=(8, 5), facecolor="#2C2F33")  # Adjusted size
        ax.set_facecolor("#3A3D41")
        sns.histplot(self.ratingsData['rating'], bins=10, kde=True, ax=ax, color='#32CD32')
        plt.title('Distribution of User Ratings', color="#FFFFFF", fontsize=14, fontweight='bold')
        plt.xlabel('User Rating (1-10)', color="#FFFFFF", fontsize=12)
        plt.ylabel('Frequency', color="#FFFFFF", fontsize=12)
        plt.xticks(color="#FFFFFF", fontsize=10)
        plt.yticks(color="#FFFFFF", fontsize=10)
        ax.grid(True, color="#555555", linestyle="--", alpha=0.7)
        plt.tight_layout()
        self.showPlot(fig, frame)

    def plotRatingComparison(self, frame):
        # Scatter plot for official vs user ratings
        fig, ax = plt.subplots(figsize=(8, 5), facecolor="#2C2F33")  # Adjusted size
        ax.set_facecolor("#3A3D41")
        # Fixed SyntaxError: completed hex color code to '#FFD700'
        sns.scatterplot(x='rating_official', y='rating_user', data=self.mergedData, ax=ax, color='#FFD700', alpha=0.6)
        plt.title('Official vs User Ratings', color="#FFFFFF", fontsize=14, fontweight='bold')
        plt.xlabel('Official Rating', color="#FFFFFF", fontsize=12)
        plt.ylabel('Average User Rating', color="#FFFFFF", fontsize=12)
        plt.xticks(color="#FFFFFF", fontsize=10)
        plt.yticks(color="#FFFFFF", fontsize=10)
        ax.grid(True, color="#555555", linestyle="--", alpha=0.7)
        plt.tight_layout()
        self.showPlot(fig, frame)

    def showPlot(self, fig, frame):
        # Helper function to display a plot in a Tkinter frame
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

# TODO: Maybe add a search bar to find specific anime? Not sure how to do that yet.
def main():
    root = tk.Tk()
    root.minsize(1200, 900)  # Increased minimum window size to fit all charts
    app = animeDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main()