import praw
import random
import threading
import time


def get_cat_facts(cat_file="cat_facts.txt"):
    """Returns a list of facts about cats from the cat file (one fact 
    per line)"""
    with open(cat_file, "r") as cat_file:
        return [line for line in cat_file]

def get_login_details(text_file):
    """Returns the three lines containing the username, password, and
    bot identification information"""
    with open(text_file, "r") as login_file:
        user = login_file.readline().strip()
        password = login_file.readline().strip()
        bot_identity_string = login_file.readline().strip()
    return user, password, bot_identity_string

def login(username, password, bot_identity_string):
    """Logs the bot into reddit using the username/password"""
    user_agent = praw.Reddit(bot_identity_string)
    user_agent.login(username, password)
    print("Authenticated", username)
    return user_agent

def get_new_posts(bot, subreddit_name, limit=10):
    """Gets the new posts from the given subreddit. The limit changes how
    many posts are taken at once, increasing it might have negative effects,
    multithreading it might be a better solution"""
    subreddit = bot.get_subreddit(subreddit_name)
    return [post for post in subreddit.get_new(limit=limit)]

def wants_a_cat_fact(comment):
    """Returns true if the comment asked for a cat fact (they said
    "catfacts" or "cat facts"""
    return any(phrase in comment.body for phrase in ("catfacts", "cat facts"))

def already_replied(bot_name, comment):
    """Returns true if the bot has already replied to the cat fact's request
    """
    return bot_name in [reply.author.name for reply in comments.replies]

def get_cat_lovers(cat_lovers_file="cat_lovers.txt"):
    """Returns a list of the cat lovers saved in the cat lovers file"""
    with open(cat_lovers_file, "r") as cat_lovers_file:
        cat_lovers = [cat_lover.strip() for cat_lover in cat_lovers_file]
        return cat_lovers

def save_cat_lovers(cat_lovers, cat_lovers_file="cat_lovers.txt"):
    with open(cat_lovers_file, "w") as cat_lovers_file:
        for name in cat_lovers:
            cat_lovers_file.write(name + "\n")

def add_to_cat_lovers_list(user, cat_lovers):
    """Adds the user to the list of cat lovers who will be provided
    interesting facts about cats"""
    if user not in cat_lovers:
        cat_lovers.append(user)

def remove_from_cat_lovers(user, cat_lovers):
    cat_lovers.remove(user)

def send_cat_fact(bot, user, fact, bot_details=""):
    message = fact + "\n" + bot_details
    bot.send_message(user, "Cat Fact", message)

def send_cat_facts_to_all(bot, cat_lovers, cat_facts_file="cat_facts.txt",
                          bot_details=""):
    """Sends random facts to all of the cat lovers"""
    facts = get_cat_facts(cat_facts_file)
    for cat_lover in cat_lovers:
        cat_lover = cat_lover.strip()
        fact = random.choice(facts)
        user = bot.get_redditor(cat_lover)
        send_cat_fact(bot, user, fact, bot_details)
    print("Sent random cat facts to cat lovers!")

if __name__ == "__main__":
    username, password, identification = get_login_details("login.txt")
    bot = login(username, password, identification)
    cat_lovers = get_cat_lovers()
    print("Retrieved saved cat lovers list")

    fact_pm_thread = threading.Timer(interval=60*60, # One hour
                                     function=send_cat_facts_to_all,
                                     args=(bot, cat_lovers))
    fact_pm_thread.start()
    subreddit = "redditbots"
    while True:
        print("Listening to the subreddit:", subreddit)
        for post in get_new_posts(bot, "all", limit=30):
            for comment in post.comments:
                if wants_a_cat_fact(comment):
                   user = comment.author
                   print("Found a cat lover:", user.name)
                   add_to_cat_lovers_list(user.name, cat_lovers)
                   save_cat_lovers(cat_lovers)
 
        time.sleep(30) # Check every 30 seconds            
