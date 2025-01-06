import game
import cProfile
import pstats

if __name__ == "__main__":
    app = game.Game()
    if game.settings.DEBUG:
        with cProfile.Profile() as pr:
            app.run()

        stats = pstats.Stats(pr)
        stats.strip_dirs()
        stats.sort_stats("cumulative")  # Options: "time", "calls", "cumulative"
        stats.print_stats()  # Print top 20 functions
    else:
        app.run()


