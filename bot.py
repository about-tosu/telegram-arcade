import configparser, threading, requests, json, re, time, sys

from uuid import uuid4

from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram import InlineQueryResultGame, InputTextMessageContent
from telegram.ext import CommandHandler, CallbackQueryHandler, InlineQueryHandler, CommandHandler
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.constants import ParseMode

class Global:
	def __init__(self):
		return

class GameHTTPRequestHandler(BaseHTTPRequestHandler):
	def __init__(self, *args):
		BaseHTTPRequestHandler.__init__(self, *args)

	def do_GET(self):
		if "#" in self.path:
			self.path = self.path.split("#")[0]
		if "?" in self.path:
			(route, params) = self.path.split("?")
		else:
			route = self.path
			params = ""
		route = route[1:]
		params = params.split("&")
		if route in Global.games:
			self.send_response(200)
			self.end_headers()
			self.wfile.write(open(route+'.html', 'rb').read())
		elif route == "setScore":
			params = {}
			for item in self.path.split("?")[1].split("&"):
				if "=" in item:
					pair = item.split("=")
					params[pair[0]] = pair[1]
			print(params)
			if "imid" in params:
				Global.bot.set_game_score(params["uid"], params["score"], inline_message_id=params["imid"])	
			else:
				Global.bot.set_game_score(params["uid"], params["score"], message_id=params["mid"], chat_id=params["cid"])
	self.send_response(200)
			self.end_headers()
			self.wfile.write(b'Set score')
		else:
			self.send_response(404)
			self.end_headers()
			self.wfile.write(b'Invalid game!')

def start(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.chat_id, Global.featured) 

def error(bot, update, error):
	print(update, error)

def button(bot, update):
	print(update)
	query = update.callback_query
	game = query.game_short_name
	uid = str(query.from_user.id)
	if query.message:
		mid = str(query.message.message_id)
		cid = str(query.message.chat.id)
		url = "http://" + Global.host + ":"+Global.port + "/" + game + "?uid="+uid+"&mid="+mid+"&cid="+cid
	else:
		imid = update.callback_query.inline_message_id
		url = "http://" + Global.host + ":"+Global.port + "/" + game + "?uid="+uid+"&imid="+imid
	print(url)
	bot.answer_callback_query(query.id, text=game, url=url)

def inlinequery(update, context):
	query = context.inline_query.query
	results = []
	for game in Global.games:
		if query.lower() in game.lower():
			results.append(InlineQueryResultGame(id=str(uuid4()),game_short_name=game))
	context.inline_query.answer(results)

def main():
	config = configparser.ConfigParser()
	config.read('config.ini')
	token = config['DEFAULT']['API_KEY']
	Global.games = config['DEFAULT']['GAMES'].split(',')
	Global.host = config['DEFAULT']['HOST']
	Global.port = config['DEFAULT']['PORT']
	Global.featured = config['DEFAULT']['FEATURED']
	application = Application.builder().token(token).build()


	application.add_handler(CommandHandler("start", start)
	application.add_handler(InlineQueryHandler(inlinequery))
	application.add_handler(CallbackQueryHandler(button))
	application.add_handler(error)
	Global.bot = application.bot

	print("Polling telegram")
	application.run_polling yg

	print("Starting http server")	
	http = HTTPServer((Global.host, int(Global.port)), GameHTTPRequestHandler)
	http.serve_forever()


if __name__ == '__main__':
	main()
