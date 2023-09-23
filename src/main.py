import data.database as database
import config

def main():
	print("============== WacK Repackager ==============")
	config.load()
	database.init()

if __name__ == '__main__':
	main()