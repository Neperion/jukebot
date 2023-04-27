import os
import bot


def main():
    bot.bot.run(os.getenv('TOKEN'))


if __name__ == '__main__':
    main()
