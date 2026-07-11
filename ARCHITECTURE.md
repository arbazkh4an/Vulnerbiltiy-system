# How VulnScan AI Works

This document explains what the project does and how its pieces fit together, without
assuming you can read code. If you just want to understand the system, start here.

## What the product does

VulnScan AI lets someone type in a website's URL and get back a security report. Under the
hood, the app probes that website the way an attacker might (but safely, without breaking
anything), looks for common weaknesses, and then uses an AI model to explain how serious each
one is and what to do about it. The result is a scan history page and a downloadable PDF
report.

## The three moving parts

Think of the system as three separate programs that all need to be running at once, plus one
shared filing cabinet (the database) they all read and write to.

1. **The website** (what visitors see and use). This is the part with the sign-up/login pages,
   the dashboard where you paste in a URL to scan, and the page that shows scan results and
   lets you download a PDF. This is also, slightly unusually, where the "submit a scan" and
   "check on a scan" requests are handled — it writes new scan requests straight into the
   database itself, rather than asking a separate server to do it.

2. **The scan engine** (a separate program, currently running quietly in the background). Its
   only job is to watch the database for new scan requests. Every few seconds it checks: "is
   there a scan waiting to be done?" When it finds one, it fetches the target URL, runs a
   battery of checks against it, asks an AI model to assess the severity of what it found, and
   writes the results back to the database.

3. **A second, independent API** (built with a framework called FastAPI). This is a fully
   working alternative front door into the same system — you could point a mobile app or some
   other client at it instead of the website. Right now, though, the website doesn't actually
   use it; it's built and functional but sitting unused alongside the other two pieces.

Because all three pieces read and write the same database, they don't need to talk to each
other directly — the database is the shared meeting point. The website drops off scan
requests, and the scan engine picks them up.

## What happens when you run a scan, step by step

1. You paste a URL into the dashboard and hit submit.
2. The website checks the URL is safe to scan (no internal/private addresses, no scanning
   things like your own home network) and records a new "queued" scan.
3. The scan engine notices the new scan request and starts working on it.
4. It runs four kinds of checks against the target site (details below), each looking for a
   different category of problem.
5. All the raw findings get handed to an AI model, which reads them and writes a plain-English
   severity assessment — how bad each issue is and what to do about it. If the AI service is
   unavailable, there's a simpler fallback that scores severity using fixed rules instead.
6. The results are saved, and the scan is marked complete.
7. Back on the results page, the website checks in every few seconds until it sees the scan is
   done, then displays the findings and lets you download a PDF report.

## The four kinds of checks it runs

- **Security headers** — checks whether the site sends the standard protective headers
  browsers rely on (things that prevent clickjacking, force HTTPS, stop content-type
  sniffing, etc.), and flags any that are missing.
- **HTTPS/certificate health** — checks whether the site is using HTTPS at all, whether its
  security certificate is expired or expiring soon, whether it's using an outdated/weak version
  of the encryption protocol, and whether it uses weak ciphers.
- **Exposed files and folders** — tries a list of common "sensitive" URLs (config files,
  admin panels, database dumps, etc.) to see if anything a site shouldn't expose is publicly
  reachable.
- **Known vulnerabilities in the software stack** — tries to identify what software/frameworks
  a site is built on (WordPress, jQuery, React, etc.) and checks a public vulnerability
  database for known security issues in those versions.

## Logging in

The website handles all sign-up/login/session management through a third-party auth service
(Clerk) — it's not custom-built. Only signed-in users can see a dashboard or submit scans.

The separate FastAPI door mentioned above has its own, simpler login check, but since nothing
currently sends it real traffic, that check hasn't been fully hardened yet — it's a loose end
to tidy up before anyone actually starts using that second door.

## What's stored

The database keeps: each scan you've run (target URL, status, when it started/finished), the
list of vulnerabilities found per scan, the AI's written assessment, and a log of consent (a
record that you agreed to have that URL scanned).

## A few known rough edges

These don't stop the product from working, but are worth knowing about:

- There are a couple of leftover, unused folders in the project (old experiments that were
  mostly deleted, just not fully cleaned up). They're not part of how the app actually runs
  today.
- There's a PDF-generating piece inside the scan engine that isn't actually used — the PDF you
  download today is generated by the website itself, through a different mechanism.
- There are two different versions of the database blueprint sitting in the project; only one
  of them matches what's actually in use.
- A small wording mismatch between two parts of the code means the "finished at" timestamp on a
  scan may not always get recorded, even though the scan itself completes correctly.
- The second, unused API door's login check isn't fully wired up to the same login system the
  website uses — fine for now since nothing calls it, but it would need attention before it's
  put into real use.

## Where to look next

- [startup guide/startup.txt](startup%20guide/startup.txt) — the three commands you run to
  start everything up locally.
