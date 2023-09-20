import os
import bot
import dotenv


def main():
    dotenv.load_dotenv()
    bot.bot.run(os.getenv('TOKEN'))


if __name__ == '__main__':
    main()
