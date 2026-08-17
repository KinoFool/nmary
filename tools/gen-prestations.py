#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genere les quatre pages prestation de nmary.net.

Ces pages partagent la meme structure (hero, Le deroule, une section propre
a la page, Facturation, Autres prestations, contact). Les ecrire a la main
les ferait diverger, donc elles sont produites ici depuis une seule source.

Le contenu de chaque page vit dans PAGES ci-dessous. La sortie est du HTML
statique ordinaire, versionne comme le reste du site : ce script n'est pas
une etape de build, on le relance seulement quand le contenu change.

Usage :
    python3 tools/gen-prestations.py            ecrit les pages
    python3 tools/gen-prestations.py --check    verifie sans ecrire

Voir README.md pour les conventions (tirets cadratins interdits, espaces
insecables, alternance des bandes).
"""
import json
import os
import re
import sys

BASE = "https://www.nmary.net"

NAV = """<nav class="nav">
  <div class="nav-inner">
    <a class="nav-logo" href="index.html">NMARY</a>
    <div class="nav-links">
      <a href="index.html#prestations">Prestations</a>
      <a href="index.html#parcours">Parcours</a>
      <a href="index.html#contact">Contact</a>
    </div>
  </div>
</nav>"""

FOOTER = """<footer class="footer">
    <div class="footer-inner">
      <div class="footer-cols">
        <div class="footer-col">
          <div class="footer-col-title">Prestations</div>
          <a href="conseil-audit.html">Conseil &amp; Audit</a>
          <a href="accompagnement-technique.html">Accompagnement technique</a>
          <a href="developpement-logiciel.html">Développement logiciel</a>
          <a href="support.html">Support</a>
        </div>
        <div class="footer-col">
          <div class="footer-col-title">Contact</div>
          <a href="mailto:contact@nmary.net">contact@nmary.net</a>
          <a href="tel:+33743732193">07 43 73 21 93</a>
          <p class="footer-addr">725 Bd Robert Barrier<br>73100 Aix-les-Bains</p>
        </div>
        <div class="footer-col">
          <div class="footer-col-title">Le site</div>
          <a href="mentions-legales.html">Mentions légales</a>
          <a href="cgv.html">CGV</a>
          <a href="https://www.linkedin.com/in/nmary/" target="_blank" rel="noopener">LinkedIn</a>
        </div>
      </div>
      <div class="footer-bottom">
        <span>Nicolas Mary · Entrepreneur Individuel · SIREN 108 324 450</span>
        <span>© 2026 <a class="footer-brand" href="https://nmary.net">NMARY.net</a></span>
      </div>
    </div>
  </footer>"""

BILLING_DAY = """<div class="card-shell"><div class="card billing">
          <p class="billing-lead">Je travaille à la journée.</p>
          <p class="billing-note">Le nombre de jours est estimé et <strong>annoncé avant de commencer</strong> : vous validez un montant, pas un compteur qui tourne. Sur les missions longues, on réajuste en cours de route, d'un commun accord.</p>
          <p class="billing-meta">Premier échange gratuit · Frais de déplacement annoncés dans le devis</p>
        </div></div>"""

ORDER = ["conseil-audit", "accompagnement-technique", "developpement-logiciel", "support"]

CARDS = {
    "conseil-audit": ("i-clipboard-check", "Conseil &amp; Audit"),
    "accompagnement-technique": ("i-tool", "Accompagnement technique"),
    "developpement-logiciel": ("i-code", "Développement logiciel"),
    "support": ("i-lifebuoy", "Support"),
}


def flow(steps):
    """steps = [(titre, description, rendu|None), ...]"""
    out = ['<ol class="flow">']
    for title, desc, rendu in steps:
        r = f'\n            <p class="flow-out"><b>Rendu</b> : {rendu}</p>' if rendu else ''
        out.append(f'          <li>\n'
                   f'            <h3 class="flow-title">{title}</h3>\n'
                   f'            <p class="flow-desc">{desc}</p>{r}\n'
                   f'          </li>')
    out.append('        </ol>')
    return "\n".join(out)


def more(slugs):
    out = ['<div class="presta-more">']
    for s in slugs:
        icon, label = CARDS[s]
        out.append(f'          <a class="card row" href="{s}.html">\n'
                   f'            <h3 class="card-title"><svg class="icon card-icon"><use href="assets/icons.svg#{icon}"/></svg><span>{label}</span></h3>\n'
                   f'          </a>')
    out.append('        </div>')
    return "\n".join(out)


CONTACT = """<div class="sec-head">
          <span class="sec-pill">Contact</span>
          <h2 class="sec-title">Un premier échange, sans engagement.</h2>
          <p class="sec-lead">Décrivez votre besoin en deux lignes, même approximativement. Je vous dis si je peux aider, et comment.</p>
        </div>
        <div class="contact-grid">
          <a class="card contact-card" href="mailto:contact@nmary.net">
            <svg class="icon contact-card-icon"><use href="assets/icons.svg#i-mail"/></svg>
            <span class="contact-card-label">Par email</span>
            <span class="contact-card-value">contact@nmary.net</span>
          </a>
          <a class="card contact-card" href="tel:+33743732193">
            <svg class="icon contact-card-icon"><use href="assets/icons.svg#i-phone"/></svg>
            <span class="contact-card-label">Par téléphone</span>
            <span class="contact-card-value">07 43 73 21 93</span>
          </a>
        </div>"""


def fix_nbsp(html):
    """Espace insecable avant : ; ! ? hors balises et hors <script>."""
    out = []
    for i, part in enumerate(re.split(r'(<script\b.*?</script>|<style\b.*?</style>)', html, flags=re.S)):
        if i % 2 == 1:
            out.append(part); continue
        segs = re.split(r'(<[^>]+>)', part)
        for j, seg in enumerate(segs):
            if j % 2 == 0:
                segs[j] = re.sub(r' +([:;!?])(?=\s|$|<)', '\u00a0\\1', seg)
        out.append(''.join(segs))
    return ''.join(out)


PAGES = [
 dict(slug="conseil-audit", num="01", icon="i-clipboard-check",
   title="Conseil &amp; Audit", sub="Système, réseau &amp; cybersécurité",
   flag="Prestation phare",
   lead="Une mission pour <strong>comprendre, sécuriser et fiabiliser</strong> votre infrastructure : réseau et firewall, serveurs Linux, sauvegardes, gestion des accès. Elle avance par étapes, et à chaque palier vous décidez si on continue.",
   doctitle="Conseil &amp; Audit informatique pour PME · NMARY",
   desc="Audit système, réseau et cybersécurité pour PME en Savoie. Cartographie, audit de configuration, plan d'action priorisé et remédiation. Premier échange gratuit.",
   ogdesc="Audit système, réseau et cybersécurité pour PME en Savoie. Cartographie, audit de configuration, plan d'action priorisé et remédiation.",
   ld=dict(name="Conseil & Audit : système, réseau & cybersécurité",
           stype="Audit informatique et cybersécurité",
           d="Mission structurée pour comprendre, sécuriser et fiabiliser l'infrastructure informatique d'une PME : cartographie, audit de configuration, plan d'action priorisé et remédiation."),
   sections=[
     dict(pill="Le déroulé", head="Quatre étapes. Vous décidez à chaque palier.", body=flow([
       ("Prévente",
        "Un appel de 30 minutes ou un rendez-vous sur site, gratuit et sans engagement, pour comprendre votre contexte et cadrer le périmètre.",
        "un devis pour l'étape suivante, et une estimation indicative pour la suite."),
       ("Cartographie",
        "On documente votre infrastructure telle qu'elle est réellement, topologie, équipements, serveurs, postes, flux et accès. C'est l'étape qui rend tout le reste chiffrable précisément.",
        "un rapport de compréhension du réseau, avec schémas."),
       ("Audit",
        "Règles de firewall, ACL, segmentation VLANs, droits et gestion des accès, sauvegardes et durcissement des serveurs, confrontés aux bonnes pratiques.",
        "les failles classées par criticité, avec un plan d'action priorisé."),
       ("Remédiation",
        "On corrige, par ordre de priorité. Vous restez maître du rythme et du périmètre, rien n'oblige à tout traiter d'un coup.",
        "la preuve du travail effectué à chaque intervention."),
     ])),
     dict(pill="Facturation", head="Un montant annoncé, pas un compteur.", body=BILLING_DAY),
   ]),

 dict(slug="accompagnement-technique", num="02", icon="i-tool",
   title="Accompagnement technique", sub="Vous avez un besoin précis, je m'en occupe",
   flag=None,
   lead="Vous savez ce qu'il vous faut, ou vous avez besoin d'un coup de main sur un point précis : je vous propose une solution adaptée, puis <strong>je la mets en place et je la configure</strong>. Sans la mission d'audit complète.",
   doctitle="Accompagnement technique IT · Mise en place &amp; configuration · NMARY",
   desc="Aide technique à la demande pour PME en Savoie : VPN et accès distant, serveur, équipement réseau, solution open source. Recommandation, mise en place, configuration et passation.",
   ogdesc="Aide technique à la demande pour PME en Savoie : VPN et accès distant, serveur, équipement réseau, solution open source.",
   ld=dict(name="Accompagnement technique",
           stype="Mise en place et configuration d'infrastructure informatique",
           d="Aide technique à la demande : recommandation d'une solution adaptée, mise en place, configuration et passation. VPN et accès distant, serveurs, équipements réseau, solutions open source."),
   sections=[
     dict(pill="Le déroulé", head="De la recommandation à la passation.", body=flow([
       ("Recommandation", "Je propose une solution adaptée à votre besoin et à votre budget, souvent open source, avec une estimation.", None),
       ("Mise en place", "Installation et déploiement.", None),
       ("Configuration", "Réglages, sécurisation, mise en service.", None),
       ("Passation", "La solution fonctionne, et vous savez vous en servir.", None),
     ])),
     dict(pill="Exemples", head="Ce que je mets en place, concrètement.", body="""<ul class="check-list">
          <li><svg class="icon"><use href="assets/icons.svg#i-shield-lock"/></svg><span><strong>VPN et accès distant sécurisé</strong> : travailler hors du bureau sans exposer votre réseau.</span></li>
          <li><svg class="icon"><use href="assets/icons.svg#i-topology"/></svg><span><strong>Serveur ou équipement réseau</strong> : installation et configuration.</span></li>
          <li><svg class="icon"><use href="assets/icons.svg#i-tool"/></svg><span><strong>Solution open source</strong> : supervision, partage de fichiers, sauvegarde.</span></li>
        </ul>
        <p class="presta-aside"><svg class="icon"><use href="assets/icons.svg#i-arrow-up-right"/></svg><span>Si votre situation demande d'abord un état des lieux, c'est plutôt le <a href="conseil-audit.html">conseil &amp; audit</a> qu'il vous faut.</span></p>"""),
     dict(pill="Facturation", head="Un montant annoncé, pas un compteur.", body=BILLING_DAY),
   ]),

 dict(slug="developpement-logiciel", num="03", icon="i-code",
   title="Développement logiciel", sub="Quand rien d'existant ne convient",
   flag=None,
   lead="Une automatisation, un outil interne, un script, une intégration entre deux systèmes. Je reste volontairement sur des <strong>développements d'appoint</strong> plutôt que sur des applications lourdes : ce que je livre doit rester vivable pour vous après mon départ.",
   doctitle="Développement logiciel sur mesure pour PME · NMARY",
   desc="Développement sur mesure pour PME en Savoie : outil interne, script, automatisation, intégration. Cadrage du besoin, développement itératif, documentation claire du code livré.",
   ogdesc="Développement sur mesure pour PME en Savoie : outil interne, script, automatisation, intégration.",
   ld=dict(name="Développement logiciel sur mesure", stype="Développement logiciel",
           d="Développement sur mesure pour les besoins non couverts par une solution existante : outil interne, script, automatisation, intégration."),
   sections=[
     dict(pill="Le déroulé", head="Du cadrage à la mise en production.", body=flow([
       ("Cadrage", "Un cahier des charges est attendu en entrée. S'il n'existe pas, je le construis avec vous, et ce travail fait partie du projet.", None),
       ("Analyse et proposition", "Choix techniques et devis.", None),
       ("Développement itératif", "Vous voyez avancer, vous pouvez réorienter.", None),
       ("Livraison", "Mise en production.", None),
     ])),
     dict(pill="Ce que vous recevez", head="Un logiciel, et de quoi le reprendre sans moi.", body="""<ul class="check-list">
          <li><svg class="icon"><use href="assets/icons.svg#i-check"/></svg><span>Un <strong>logiciel fonctionnel</strong>, livré et mis en service.</span></li>
          <li><svg class="icon"><use href="assets/icons.svg#i-file-text"/></svg><span>Une <strong>documentation claire de tout le code produit</strong>, suivant la pratique <a href="https://arc42.org" target="_blank" rel="noopener">arc42</a>. Un autre prestataire peut reprendre le travail.</span></li>
          <li><svg class="icon"><use href="assets/icons.svg#i-check"/></svg><span>Les éléments de <strong>configuration et d'usage</strong> nécessaires à l'exploitation.</span></li>
        </ul>
        <p class="presta-aside"><svg class="icon"><use href="assets/icons.svg#i-arrow-up-right"/></svg><span>Et si une solution du marché suffit, je vous le dis : ce sera moins cher, et cela relèvera de l'<a href="accompagnement-technique.html">accompagnement technique</a>.</span></p>"""),
     dict(pill="Facturation", head="Un montant annoncé, pas un compteur.", body="""<div class="card-shell"><div class="card billing">
          <p class="billing-lead">Je travaille à la journée.</p>
          <p class="billing-note">Le nombre de jours est estimé et <strong>annoncé avant de commencer</strong> : vous validez un montant, pas un compteur qui tourne. Le temps d'analyse et de choix techniques compte comme du développement, il est dans l'estimation.</p>
          <p class="billing-meta">Premier échange gratuit</p>
        </div></div>"""),
   ]),

 dict(slug="support", num="04", icon="i-lifebuoy",
   title="Support", sub="Une aide ponctuelle, quand vous en avez besoin",
   flag=None,
   lead="Un problème, une question, quelque chose qui ne fonctionne plus : j'interviens ponctuellement, à distance ou sur site, <strong>sans contrat ni abonnement</strong>.",
   doctitle="Support informatique ponctuel pour PME · NMARY",
   desc="Support informatique ponctuel pour PME en Savoie : une aide quand vous en avez besoin, sans contrat de maintenance ni abonnement.",
   ogdesc="Support informatique ponctuel pour PME en Savoie, sans contrat de maintenance ni abonnement.",
   ld=dict(name="Support informatique ponctuel", stype="Support et dépannage informatique",
           d="Aide ponctuelle en cas de problème informatique, sans contrat de maintenance récurrent."),
   sections=[
     dict(pill="Le déroulé", head="Trois étapes, sans engagement.", body=flow([
       ("Vous me décrivez le problème", "Par email ou par téléphone.", None),
       ("Je vous réponds", "Si je peux aider, et sous quel délai.", None),
       ("J'interviens", "À distance, ou sur site quand c'est nécessaire.", None),
     ])),
     dict(pill="Le cadre", head="Ce que le support n'est pas.", body="""<div class="prose">
          <p class="presta-text">Je ne propose pas, à ce jour, de <strong>contrat de maintenance ni d'accompagnement récurrent</strong>. Si vous cherchez une infogérance complète avec astreinte et engagements de délai, je ne suis pas le bon interlocuteur.</p>
          <p class="presta-text">Le support est surtout efficace quand je connais déjà votre infrastructure, à la suite d'un <a href="conseil-audit.html">audit</a> ou d'un <a href="accompagnement-technique.html">accompagnement</a>. Une première demande isolée reste possible.</p>
        </div>"""),
     dict(pill="Facturation", head="Au temps passé, annoncé d'avance.", body="""<div class="card-shell"><div class="card billing">
          <p class="billing-lead">Au temps passé.</p>
          <p class="billing-note">Selon l'ampleur : à l'heure, à la demi-journée ou à la journée. Le volume estimé vous est <strong>annoncé avant l'intervention</strong>.</p>
          <p class="billing-meta">Frais de déplacement annoncés à l'avance</p>
        </div></div>"""),
   ]),
]


def render(p):
    ld = {
        "@context": "https://schema.org", "@type": "Service",
        "name": p["ld"]["name"], "serviceType": p["ld"]["stype"],
        "description": p["ld"]["d"], "url": f"{BASE}/{p['slug']}.html",
        "provider": {"@type": "ProfessionalService", "name": "NMARY", "url": BASE},
        "areaServed": ["Aix-les-Bains", "Chambéry", "Annecy", "Savoie", "Haute-Savoie"],
        "audience": {"@type": "BusinessAudience", "name": "TPE et PME"},
    }
    flag = ""
    if p["flag"]:
        flag = f'\n        <p class="presta-flag"><svg class="icon"><use href="assets/icons.svg#i-shield-lock"/></svg>{p["flag"]}</p>'

    # alternance stricte : le hero est clair, la 1re bande est foncee, puis on alterne
    # sur la totalite des bandes, section specifique + "autres" + contact comprises.
    def tone(i):
        return " band-alt" if i % 2 == 0 else ""

    bands = []
    for i, s in enumerate(p["sections"]):
        alt = tone(i)
        bands.append(f"""    <section class="band{alt}">
      <div class="band-inner">
        <div class="sec-head">
          <span class="sec-pill">{s['pill']}</span>
          <h2 class="sec-title">{s['head']}</h2>
        </div>
        {s['body']}
      </div>
    </section>""")

    n = len(p["sections"])
    bands.append(f"""    <section class="band{tone(n)}">
      <div class="band-inner">
        <div class="sec-head">
          <span class="sec-pill">Autres prestations</span>
          <h2 class="sec-title">Voir aussi.</h2>
        </div>
        {more([x for x in ORDER if x != p['slug']])}
      </div>
    </section>""")

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{p['doctitle']}</title>
<link rel="icon" type="image/svg+xml" href="assets/svg/NM.svg">
<meta name="description" content="{p['desc']}">
<link rel="canonical" href="{BASE}/{p['slug']}.html">
<meta property="og:type" content="website">
<meta property="og:site_name" content="NMARY">
<meta property="og:locale" content="fr_FR">
<meta property="og:url" content="{BASE}/{p['slug']}.html">
<meta property="og:title" content="{p['doctitle']}">
<meta property="og:description" content="{p['ogdesc']}">
<meta property="og:image" content="{BASE}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="assets/fonts/space-grotesk-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/style.css">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
<div class="page">
{NAV}
  <main>

    <div class="band presta-hero">
      <div class="band-inner">
        <a href="index.html#prestations" class="back-link"><svg class="icon"><use href="assets/icons.svg#i-arrow-left"/></svg>Retour aux prestations</a>
        <header class="presta-header">
          <div class="presta-eyebrow">
            <svg class="icon"><use href="assets/icons.svg#{p['icon']}"/></svg>
            <span>Prestation {p['num']}</span>
          </div>
          <h1 class="presta-title">{p['title']}</h1>
          <p class="presta-sub">{p['sub']}</p>{flag}
          <p class="presta-lead">{p['lead']}</p>
        </header>
      </div>
    </div>

{chr(10).join(bands)}

    <section class="band{tone(n + 1)}" id="contact">
      <div class="band-inner">
        {CONTACT}
      </div>
    </section>

  </main>

  {FOOTER}
</div>
</body>
</html>
"""


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    check = "--check" in sys.argv
    drift = []
    for p in PAGES:
        out = os.path.join(ROOT, p["slug"] + ".html")
        html = fix_nbsp(render(p))
        if "\u2014" in html or "\u2013" in html:
            sys.exit("tiret cadratin dans " + p["slug"])
        if check:
            current = open(out, encoding="utf-8").read() if os.path.exists(out) else ""
            state = "a jour" if current == html else "DIVERGE"
            if current != html:
                drift.append(p["slug"])
            print(f"{p['slug'] + '.html':32} {state}")
        else:
            open(out, "w", encoding="utf-8").write(html)
            print("ecrit", p["slug"] + ".html")
    if check and drift:
        sys.exit(f"\n{len(drift)} page(s) a regenerer : " + ", ".join(drift))


if __name__ == "__main__":
    main()
