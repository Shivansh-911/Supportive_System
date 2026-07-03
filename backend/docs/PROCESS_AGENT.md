## Process Agent

Central orchestrator of the ingestion pipeline. Activated by the outbox poller on every approved sync event.

the process agent will be called by an outbox worker that will take scan the sync_events table and call the process event via an ingent_one function and send the event.

So we are now implementing the ingestion pipeline with the help of factory pattern 

each source will have a factory which will have a ingestion_pipeline for that 

right now focus on the ingestion pipeline for freshdesk help docs as follows

content hash -> cleaning -> convert to markdown -> source metadata creation -> store it in document_store -> replace image urls with [img no] -> chunking -> chunk image map -> context_prefix -> chunk metadata -> searchable text -> embedding

it will first select the llm and embedding model to be used from the name writtern in the constants.py

content hash => it will generate and check the content hash and decide if we want to skip or proceed also set the values in the sync_event accordingly

cleaning for fresh desk => will take the raw json from the pipeline model and then clean the html content of the fresh desk 

convert to markdown for fresh desk => will take the previous cleaned html from the pipeline model and then will convert it into markdown

source metadata creation => combine all important feilds of a source into a metadata

store in document_store => will populate the document store

replace image url with [img] => as we will be also processing images into chunks but the image url add a lot of tokens and decreases the semantic meaning so replace it with a placeholder and store the mapping

chunking for freshdesk => it will take the strucutred json format and then apply the chunking stratergy based on the document either heading aware or recurrsive

chunk image map => Take the document image map and create a chunk image map for each chunk 

context _prefix => will call the context_retrieval class to get the context of the chunk 

chunk metadata => add contents to the chunk metadata

searchable_text for freshdesk => will take the category name, folder name, article title, section heading and context prefix and then attach all of these to each chunk content 

embedding => will convert embedding for each chunk and store it in the chunking table 




Cleaning => 
Parse `description` (HTML) with BeautifulSoup using the `lxml` parser (faster and stricter than `html.parser` — required for Freshdesk's malformed HTML). Cleaning produces **two outputs** used downstream:
- **cleaned_html** — structure preserved (`<h2>`, `<h3>`, `<p>`, `<ul>/<li>`, `<div>`, `<section>`), used by step 6 to build the heading tree.
- **cleaned_text** — plain text extracted from cleaned_html, persisted to `document_store.cleaned_text` (step 7).

Cleaning rules (applied to both outputs):
- Strip all `data-*` attributes (Freshdesk leaves `data-identifyelement` everywhere).
- Unwrap `<span>`,`<font>`,`<strong>`,`<figure>` wrappers — they carry only inline style noise, no semantic value.
- Decode `&nbsp;` → space; collapse runs of whitespace to single space.
- Remove zero-content nodes: empty `<h2></h2>`, `<p></p>`, `<br>`-only paragraphs.


Chunking Stratergies => 
1. heading_aware => it will take the entire document and then split the document with respect to sections 
  each chunk should be between a set no of tokens, implemeted when `heading_aware` = true
  edge cases => 
  1. if the entire document is less than max chunk words then allow it to be in a single chunk 
  2. if the last chunk in the document is less than min chunk words then add it to the previous chunk 
  3. drop sections with body chars = 0

2 recursive => chunk the cleaned text where each token is less than 400 with a 50 token ovelap













