from django.http import HttpResponse
from django.shortcuts import render #
def index(request):
    params ={'name':'Bishal','place':'Earth' }
    return render(request, 'index.html') #rendering html file
    #  HttpResponse("Home ")
# def removepunc(request):
#     djtext = request.GET.get('text', 'default')
#     # For now, just return the text received (placeholder)
#     return HttpResponse(f"Remove Punctuation: {djtext}")

# def capitalize(request):
#     return HttpResponse("capitalize first")

# def removeline(request):
#     return HttpResponse("remove line")  
# def spaceremove(request):
#     return HttpResponse("space remove <a href='/'>back</a>") 
# def charcount(request):
#     return HttpResponse("char count")
# # def about(request):
# #     return HttpResponse('hello from about page')    
def analyze(request):
    djtext = request.GET.get('text', 'default')
    removeunc = request.GET.get('removepunc', 'off')
    fullcaps = request.GET.get('fullcaps', 'off')
    newlineremover = request.GET.get('newlineremover', 'off')
    analyzed = djtext

    if removeunc == "on":
        punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        analyzed = ""
        for char in djtext:
            if char not in punctuations:
                analyzed += char
        djtext = analyzed
    
    if fullcaps == "on":
        analyzed = ""
        for char in djtext:
            analyzed += char.upper()
        djtext = analyzed

    if newlineremover == "on":
        analyzed = ""
        for char in djtext:
            if char != "\n" and char != "\r":
                analyzed += char
        djtext = analyzed

    if removeunc == "on" or fullcaps == "on" or newlineremover == "on":
        return render(request, 'analyze.html', {'analyzed_text': djtext})
    else:
        return HttpResponse("Error: No operation selected.")