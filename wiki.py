import wikipedia 


def page(title):
	page = wikipedia.page(title)
	return {
	"t": page.title,
	"d": page.content
	}