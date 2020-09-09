import wikipedia 


def page(title):
	page = wikipedia.page(title)
	return page.content