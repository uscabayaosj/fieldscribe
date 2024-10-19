import React from 'react';
import { Button } from "./components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./components/ui/card"
import { Input } from "./components/ui/input"
import { ScrollArea } from "./components/ui/scroll-area"
import { PlusCircle, Edit2 } from "lucide-react"

export default function FieldScribePro() {
  const entries = [
    {
      title: "My Fourth Journal Entry",
      date: "September 13, 2024 at 03:05 PM GMT+8",
      content: "This is another test for the timestamps. I am writing a new entry in this fieldnote app.",
    },
    {
      title: "My Third Journal Entry",
      date: "September 13, 2024 at 02:03 PM GMT+8",
      content: "I'm currently testing this journal app to see if it could be used as an ethnographic fieldnote app.",
    },
    {
      title: "My Second Fieldnote Entry",
      date: "September 13, 2024 at 03:05 PM GMT+8",
      content: "I hope I can use this for fieldnotes. Yehey!",
    },
    {
      title: "My First Journal Entry",
      date: "September 13, 2024 at 01:29 PM GMT+8",
      content: "This is the content of my first journal entry",
    },
    {
      title: "Test Entry 1",
      date: "September 13, 2024 at 01:23 PM GMT+8",
      content: "Hello World! This is an edited entry.",
    },
  ]

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-primary text-primary-foreground p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">FieldScribe Pro</h1>
          <nav>
            <Button variant="ghost" className="text-primary-foreground">Dashboard</Button>
            <Button variant="ghost" className="text-primary-foreground">New Entry</Button>
            <Button variant="ghost" className="text-primary-foreground">Logout</Button>
          </nav>
        </div>
      </header>
      <main className="container mx-auto py-8">
        <h2 className="text-3xl font-bold mb-6">Your Fieldnote Entries</h2>
        <div className="mb-6">
          <Button>
            <PlusCircle className="mr-2 h-4 w-4" /> Create New Entry
          </Button>
        </div>
        <ScrollArea className="h-[600px] rounded-md border">
          <div className="grid gap-4 p-4">
            {entries.map((entry, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle>{entry.title}</CardTitle>
                  <CardDescription>{entry.date}</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{entry.content}</p>
                </CardContent>
                <CardFooter className="flex justify-between">
                  <Button variant="outline">Read more</Button>
                  <Button variant="ghost">
                    <Edit2 className="mr-2 h-4 w-4" /> Edit
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </ScrollArea>
      </main>
    </div>
  )
}
