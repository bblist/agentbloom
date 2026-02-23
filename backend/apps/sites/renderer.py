"""
Page Renderer — Converts JSON content_blocks to responsive HTML + CSS.

Each block type has a render function that generates semantic HTML with
scoped CSS classes. The renderer produces a full page or individual block HTML.
"""

import json
import html as html_lib
from typing import Optional

# ─── CSS Reset & Base Styles ────────────────────────────────────────────────

BASE_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{font-family:var(--font-body,'Inter',system-ui,-apple-system,sans-serif);
  color:var(--text,'#1E293B');background:var(--background,'#FFFFFF');
  line-height:1.6;-webkit-font-smoothing:antialiased}
img{max-width:100%;height:auto;display:block}
a{color:var(--primary,'#2563EB');text-decoration:none}
a:hover{text-decoration:underline}
h1,h2,h3,h4,h5,h6{font-family:var(--font-heading,'Inter',sans-serif);
  line-height:1.2;color:var(--text,'#1E293B')}
.container{width:100%;max-width:var(--max-width,1280px);margin:0 auto;padding:0 1.5rem}
.section{padding:4rem 0}
.btn{display:inline-flex;align-items:center;justify-content:center;padding:0.75rem 1.5rem;
  border-radius:var(--radius-md,0.5rem);font-weight:600;cursor:pointer;
  transition:all 0.2s;border:none;font-size:1rem;text-decoration:none}
.btn-primary{background:var(--primary,'#2563EB');color:#fff}
.btn-primary:hover{opacity:0.9;text-decoration:none}
.btn-secondary{background:var(--secondary,'#7C3AED');color:#fff}
.btn-outline{background:transparent;border:2px solid var(--primary,'#2563EB');color:var(--primary,'#2563EB')}
.btn-outline:hover{background:var(--primary,'#2563EB');color:#fff;text-decoration:none}
@media(max-width:768px){.section{padding:2.5rem 0}}
"""

# ─── Block Renderers ────────────────────────────────────────────────────────


def _esc(text: str) -> str:
    """Escape HTML entities."""
    return html_lib.escape(str(text)) if text else ""


def _style_attr(styles: dict) -> str:
    """Convert style dict to inline style attribute."""
    if not styles:
        return ""
    pairs = ";".join(f"{k}:{v}" for k, v in styles.items())
    return f' style="{pairs}"'


def render_hero(block: dict) -> str:
    props = block.get("props", {})
    styles = block.get("styles", {})
    bid = block.get("id", "hero")

    headline = _esc(props.get("headline", ""))
    sub = _esc(props.get("subheadline", ""))
    cta_text = _esc(props.get("cta_text", ""))
    cta_url = _esc(props.get("cta_url", "#"))
    bg_img = props.get("background_image", "")
    overlay = props.get("overlay_color", "rgba(0,0,0,0.5)")
    alignment = props.get("alignment", "center")

    bg_style = f'background-image:url({bg_img});background-size:cover;background-position:center;' if bg_img else ''

    return f"""<section id="{bid}" class="ab-hero section"{_style_attr(styles)}>
  <div class="ab-hero__bg" style="{bg_style}">
    <div class="ab-hero__overlay" style="background:{overlay}"></div>
    <div class="container ab-hero__content" style="text-align:{alignment}">
      <h1 class="ab-hero__title">{headline}</h1>
      {"<p class='ab-hero__sub'>" + sub + "</p>" if sub else ""}
      {"<a href='" + cta_url + "' class='btn btn-primary ab-hero__cta'>" + cta_text + "</a>" if cta_text else ""}
    </div>
  </div>
</section>"""


def render_text(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "text")
    heading = _esc(props.get("heading", ""))
    body = props.get("body", "")
    alignment = props.get("alignment", "left")

    return f"""<section id="{bid}" class="ab-text section">
  <div class="container" style="text-align:{alignment}">
    {"<h2 class='ab-text__heading'>" + heading + "</h2>" if heading else ""}
    <div class="ab-text__body">{body}</div>
  </div>
</section>"""


def render_image(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "img")
    src = _esc(props.get("src", ""))
    alt = _esc(props.get("alt", ""))
    caption = _esc(props.get("caption", ""))

    return f"""<section id="{bid}" class="ab-image section">
  <div class="container">
    <figure>
      <img src="{src}" alt="{alt}" loading="lazy" />
      {"<figcaption>" + caption + "</figcaption>" if caption else ""}
    </figure>
  </div>
</section>"""


def render_cta(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "cta")
    headline = _esc(props.get("headline", ""))
    body = _esc(props.get("body", ""))
    btn_text = _esc(props.get("button_text", "Get Started"))
    btn_url = _esc(props.get("button_url", "#"))
    variant = props.get("variant", "primary")

    return f"""<section id="{bid}" class="ab-cta section" style="background:var(--surface,'#F8FAFC')">
  <div class="container" style="text-align:center">
    <h2>{headline}</h2>
    {"<p>" + body + "</p>" if body else ""}
    <a href="{btn_url}" class="btn btn-{variant}" style="margin-top:1.5rem">{btn_text}</a>
  </div>
</section>"""


def render_features(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "features")
    heading = _esc(props.get("heading", ""))
    subheading = _esc(props.get("subheading", ""))
    items = props.get("items", [])
    layout = props.get("layout", "grid")
    cols = 3 if layout == "grid" else 1

    items_html = ""
    for item in items:
        icon = _esc(item.get("icon", "✦"))
        title = _esc(item.get("title", ""))
        desc = _esc(item.get("description", ""))
        items_html += f"""<div class="ab-feature-card">
      <div class="ab-feature-card__icon">{icon}</div>
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>\n"""

    return f"""<section id="{bid}" class="ab-features section">
  <div class="container">
    {"<h2 style='text-align:center;margin-bottom:0.5rem'>" + heading + "</h2>" if heading else ""}
    {"<p style='text-align:center;color:var(--text-light);margin-bottom:2rem'>" + subheading + "</p>" if subheading else ""}
    <div class="ab-features__grid" style="display:grid;grid-template-columns:repeat({cols},1fr);gap:2rem">
      {items_html}
    </div>
  </div>
</section>"""


def render_pricing(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "pricing")
    heading = _esc(props.get("heading", "Pricing"))
    tiers = props.get("tiers", [])

    tiers_html = ""
    for tier in tiers:
        name = _esc(tier.get("name", ""))
        price = _esc(str(tier.get("price", "")))
        period = _esc(tier.get("period", "/mo"))
        features = tier.get("features", [])
        cta = _esc(tier.get("cta_text", "Choose Plan"))
        highlighted = tier.get("highlighted", False)
        hl_class = " ab-pricing__tier--highlighted" if highlighted else ""

        features_html = "".join(f"<li>✓ {_esc(f)}</li>" for f in features)
        tiers_html += f"""<div class="ab-pricing__tier{hl_class}">
      <h3>{name}</h3>
      <div class="ab-pricing__price"><span class="ab-pricing__amount">{price}</span>{period}</div>
      <ul>{features_html}</ul>
      <a href="#" class="btn {'btn-primary' if highlighted else 'btn-outline'}">{cta}</a>
    </div>\n"""

    return f"""<section id="{bid}" class="ab-pricing section">
  <div class="container">
    <h2 style="text-align:center;margin-bottom:2rem">{heading}</h2>
    <div class="ab-pricing__grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:2rem;align-items:start">
      {tiers_html}
    </div>
  </div>
</section>"""


def render_testimonials(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "testimonials")
    heading = _esc(props.get("heading", "What Our Clients Say"))
    items = props.get("items", [])

    items_html = ""
    for item in items:
        quote = _esc(item.get("quote", ""))
        author = _esc(item.get("author", ""))
        role = _esc(item.get("role", ""))
        company = _esc(item.get("company", ""))
        rating = int(item.get("rating", 5))
        stars = "★" * rating + "☆" * (5 - rating)

        items_html += f"""<div class="ab-testimonial-card">
      <div class="ab-testimonial-card__stars">{stars}</div>
      <blockquote>"{quote}"</blockquote>
      <div class="ab-testimonial-card__author">
        <strong>{author}</strong>
        {"<span>" + role + (", " + company if company else "") + "</span>" if role else ""}
      </div>
    </div>\n"""

    return f"""<section id="{bid}" class="ab-testimonials section" style="background:var(--surface,'#F8FAFC')">
  <div class="container">
    <h2 style="text-align:center;margin-bottom:2rem">{heading}</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:2rem">
      {items_html}
    </div>
  </div>
</section>"""


def render_faq(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "faq")
    heading = _esc(props.get("heading", "Frequently Asked Questions"))
    items = props.get("items", [])

    items_html = ""
    for i, item in enumerate(items):
        q = _esc(item.get("question", ""))
        a = _esc(item.get("answer", ""))
        items_html += f"""<details class="ab-faq__item">
      <summary>{q}</summary>
      <p>{a}</p>
    </details>\n"""

    return f"""<section id="{bid}" class="ab-faq section">
  <div class="container" style="max-width:800px">
    <h2 style="text-align:center;margin-bottom:2rem">{heading}</h2>
    {items_html}
  </div>
</section>"""


def render_form(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "form")
    title = _esc(props.get("title", "Contact Us"))
    desc = _esc(props.get("description", ""))
    fields = props.get("fields", [])
    submit_text = _esc(props.get("submit_text", "Submit"))

    fields_html = ""
    for field in fields:
        name = _esc(field.get("name", ""))
        ftype = field.get("type", "text")
        label = _esc(field.get("label", name))
        required = " required" if field.get("required") else ""
        placeholder = _esc(field.get("placeholder", ""))

        if ftype == "textarea":
            fields_html += f"""<div class="ab-form__field">
        <label for="{name}">{label}</label>
        <textarea id="{name}" name="{name}" placeholder="{placeholder}"{required} rows="4"></textarea>
      </div>\n"""
        elif ftype == "select":
            options_html = "".join(f"<option>{_esc(o)}</option>" for o in field.get("options", []))
            fields_html += f"""<div class="ab-form__field">
        <label for="{name}">{label}</label>
        <select id="{name}" name="{name}"{required}>{options_html}</select>
      </div>\n"""
        else:
            fields_html += f"""<div class="ab-form__field">
        <label for="{name}">{label}</label>
        <input type="{ftype}" id="{name}" name="{name}" placeholder="{placeholder}"{required} />
      </div>\n"""

    return f"""<section id="{bid}" class="ab-form section">
  <div class="container" style="max-width:640px">
    <h2 style="text-align:center">{title}</h2>
    {"<p style='text-align:center;margin-bottom:1.5rem'>" + desc + "</p>" if desc else ""}
    <form class="ab-form__form">
      {fields_html}
      <button type="submit" class="btn btn-primary" style="width:100%;margin-top:1rem">{submit_text}</button>
    </form>
  </div>
</section>"""


def render_gallery(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "gallery")
    heading = _esc(props.get("heading", ""))
    images = props.get("images", [])
    columns = props.get("columns", 3)

    imgs_html = ""
    for img in images:
        src = _esc(img.get("src", ""))
        alt = _esc(img.get("alt", ""))
        cap = _esc(img.get("caption", ""))
        imgs_html += f"""<figure class="ab-gallery__item">
      <img src="{src}" alt="{alt}" loading="lazy" />
      {"<figcaption>" + cap + "</figcaption>" if cap else ""}
    </figure>\n"""

    return f"""<section id="{bid}" class="ab-gallery section">
  <div class="container">
    {"<h2 style='text-align:center;margin-bottom:2rem'>" + heading + "</h2>" if heading else ""}
    <div style="display:grid;grid-template-columns:repeat({columns},1fr);gap:1rem">
      {imgs_html}
    </div>
  </div>
</section>"""


def render_stats(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "stats")
    heading = _esc(props.get("heading", ""))
    items = props.get("items", [])

    items_html = ""
    for item in items:
        value = _esc(str(item.get("value", "")))
        label = _esc(item.get("label", ""))
        items_html += f"""<div class="ab-stat" style="text-align:center">
      <div class="ab-stat__value" style="font-size:2.5rem;font-weight:800;color:var(--primary)">{value}</div>
      <div class="ab-stat__label">{label}</div>
    </div>\n"""

    return f"""<section id="{bid}" class="ab-stats section" style="background:var(--surface)">
  <div class="container">
    {"<h2 style='text-align:center;margin-bottom:2rem'>" + heading + "</h2>" if heading else ""}
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:2rem">
      {items_html}
    </div>
  </div>
</section>"""


def render_video(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "video")
    url = _esc(props.get("url", ""))
    title = _esc(props.get("title", ""))

    # Support YouTube embeds
    if "youtube.com/watch" in url:
        video_id = url.split("v=")[-1].split("&")[0]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
    elif "youtu.be/" in url:
        video_id = url.split("/")[-1]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
    else:
        embed_url = url

    return f"""<section id="{bid}" class="ab-video section">
  <div class="container" style="max-width:960px">
    {"<h2 style='text-align:center;margin-bottom:1.5rem'>" + title + "</h2>" if title else ""}
    <div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:var(--radius-lg,0.75rem)">
      <iframe src="{embed_url}" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0"
        allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture"
        allowfullscreen loading="lazy"></iframe>
    </div>
  </div>
</section>"""


def render_contact(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "contact")
    heading = _esc(props.get("heading", "Contact Us"))
    email = _esc(props.get("email", ""))
    phone = _esc(props.get("phone", ""))
    address = _esc(props.get("address", ""))

    return f"""<section id="{bid}" class="ab-contact section">
  <div class="container" style="max-width:800px">
    <h2 style="text-align:center;margin-bottom:2rem">{heading}</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:2rem;text-align:center">
      {"<div><strong>Email</strong><br><a href='mailto:" + email + "'>" + email + "</a></div>" if email else ""}
      {"<div><strong>Phone</strong><br><a href='tel:" + phone + "'>" + phone + "</a></div>" if phone else ""}
      {"<div><strong>Address</strong><br>" + address + "</div>" if address else ""}
    </div>
  </div>
</section>"""


def render_team(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "team")
    heading = _esc(props.get("heading", "Our Team"))
    members = props.get("members", [])

    members_html = ""
    for m in members:
        name = _esc(m.get("name", ""))
        role = _esc(m.get("role", ""))
        bio = _esc(m.get("bio", ""))
        img = _esc(m.get("image_url", ""))

        members_html += f"""<div class="ab-team-member" style="text-align:center">
      {"<img src='" + img + "' alt='" + name + "' style='width:120px;height:120px;border-radius:50%;object-fit:cover;margin:0 auto 1rem' />" if img else ""}
      <h3 style="margin-bottom:0.25rem">{name}</h3>
      <p style="color:var(--primary);font-weight:500;margin-bottom:0.5rem">{role}</p>
      {"<p style='color:var(--text-light);font-size:0.875rem'>" + bio + "</p>" if bio else ""}
    </div>\n"""

    return f"""<section id="{bid}" class="ab-team section">
  <div class="container">
    <h2 style="text-align:center;margin-bottom:2rem">{heading}</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:2rem">
      {members_html}
    </div>
  </div>
</section>"""


def render_newsletter(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "newsletter")
    heading = _esc(props.get("heading", "Stay Updated"))
    desc = _esc(props.get("description", ""))
    placeholder = _esc(props.get("placeholder", "Enter your email"))
    btn_text = _esc(props.get("button_text", "Subscribe"))

    return f"""<section id="{bid}" class="ab-newsletter section" style="background:var(--primary);color:#fff">
  <div class="container" style="max-width:640px;text-align:center">
    <h2 style="color:#fff">{heading}</h2>
    {"<p style='opacity:0.9;margin-bottom:1.5rem'>" + desc + "</p>" if desc else ""}
    <form style="display:flex;gap:0.5rem;max-width:480px;margin:0 auto" onsubmit="event.preventDefault()">
      <input type="email" placeholder="{placeholder}" style="flex:1;padding:0.75rem 1rem;border:none;border-radius:var(--radius-md)" required />
      <button type="submit" class="btn" style="background:#fff;color:var(--primary);white-space:nowrap">{btn_text}</button>
    </form>
  </div>
</section>"""


def render_footer(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "footer")
    columns = props.get("columns", [])
    copyright_text = _esc(props.get("copyright", ""))
    social = props.get("social_links", [])

    cols_html = ""
    for col in columns:
        title = _esc(col.get("title", ""))
        links = col.get("links", [])
        links_html = "".join(
            f"<li><a href='{_esc(l.get('url', '#'))}'>{_esc(l.get('text', ''))}</a></li>"
            for l in links
        )
        cols_html += f"""<div>
      <h4>{title}</h4>
      <ul style="list-style:none;margin-top:0.75rem">{links_html}</ul>
    </div>\n"""

    social_html = ""
    if social:
        social_items = "".join(
            f"<a href='{_esc(s.get('url', '#'))}' style='margin:0 0.5rem'>{_esc(s.get('platform', ''))}</a>"
            for s in social
        )
        social_html = f"<div style='margin-top:1.5rem'>{social_items}</div>"

    return f"""<footer id="{bid}" class="ab-footer" style="background:var(--text,'#1E293B');color:#fff;padding:3rem 0 1.5rem">
  <div class="container">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:2rem">
      {cols_html}
    </div>
    {social_html}
    {"<p style='text-align:center;margin-top:2rem;opacity:0.6;font-size:0.875rem'>" + copyright_text + "</p>" if copyright_text else ""}
  </div>
</footer>"""


def render_logo_cloud(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "logos")
    heading = _esc(props.get("heading", "Trusted By"))
    logos = props.get("logos", [])

    logos_html = "".join(
        f"<a href='{_esc(l.get('url', '#'))}' style='display:flex;align-items:center;justify-content:center'>"
        f"<img src='{_esc(l.get('image_url', ''))}' alt='{_esc(l.get('name', ''))}' style='max-height:48px;opacity:0.7;filter:grayscale(1);transition:all 0.3s' /></a>"
        for l in logos
    )

    return f"""<section id="{bid}" class="ab-logos section">
  <div class="container">
    {"<h2 style='text-align:center;margin-bottom:2rem;font-size:1.25rem;color:var(--text-light)'>" + heading + "</h2>" if heading else ""}
    <div style="display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:3rem">
      {logos_html}
    </div>
  </div>
</section>"""


def render_blog_feed(block: dict) -> str:
    props = block.get("props", {})
    bid = block.get("id", "blog")
    heading = _esc(props.get("heading", "Latest Posts"))

    return f"""<section id="{bid}" class="ab-blog section">
  <div class="container">
    <h2 style="text-align:center;margin-bottom:2rem">{heading}</h2>
    <div class="ab-blog__feed" data-feed="true" data-count="{props.get('count', 3)}">
      <p style="text-align:center;color:var(--text-light)">Blog posts will appear here.</p>
    </div>
  </div>
</section>"""


# ─── Block Type → Renderer Map ──────────────────────────────────────────────

BLOCK_RENDERERS = {
    "hero": render_hero,
    "text": render_text,
    "image": render_image,
    "cta": render_cta,
    "features": render_features,
    "pricing": render_pricing,
    "testimonials": render_testimonials,
    "faq": render_faq,
    "form": render_form,
    "gallery": render_gallery,
    "stats": render_stats,
    "video": render_video,
    "contact": render_contact,
    "team": render_team,
    "newsletter": render_newsletter,
    "footer": render_footer,
    "logo_cloud": render_logo_cloud,
    "blog_feed": render_blog_feed,
}


# ─── Component CSS ──────────────────────────────────────────────────────────

COMPONENT_CSS = """
.ab-hero__bg{position:relative;min-height:60vh;display:flex;align-items:center}
.ab-hero__overlay{position:absolute;inset:0}
.ab-hero__content{position:relative;z-index:1;padding:4rem 1.5rem}
.ab-hero__title{font-size:clamp(2rem,5vw,3.5rem);margin-bottom:1rem}
.ab-hero__sub{font-size:1.25rem;margin-bottom:2rem;opacity:0.9}
.ab-hero__bg:not([style*="background-image"]) .ab-hero__content{color:var(--text)}
.ab-hero__bg[style*="background-image"] .ab-hero__content{color:#fff}

.ab-feature-card{padding:2rem;border-radius:var(--radius-lg,0.75rem);background:var(--background);
  box-shadow:var(--shadow-sm,0 1px 2px rgba(0,0,0,0.05));border:1px solid var(--border,#E2E8F0)}
.ab-feature-card__icon{font-size:2rem;margin-bottom:1rem}
.ab-feature-card h3{margin-bottom:0.5rem}

.ab-pricing__tier{padding:2rem;border-radius:var(--radius-lg,0.75rem);background:var(--background);
  border:1px solid var(--border,#E2E8F0);text-align:center}
.ab-pricing__tier--highlighted{border-color:var(--primary);box-shadow:0 0 0 2px var(--primary);transform:scale(1.02)}
.ab-pricing__price{font-size:2.5rem;font-weight:800;margin:1rem 0;color:var(--text)}
.ab-pricing__tier ul{list-style:none;text-align:left;margin:1.5rem 0}
.ab-pricing__tier li{padding:0.5rem 0;border-bottom:1px solid var(--border,#E2E8F0)}

.ab-testimonial-card{padding:2rem;border-radius:var(--radius-lg);background:var(--background);
  border:1px solid var(--border,#E2E8F0)}
.ab-testimonial-card__stars{color:#F59E0B;font-size:1.25rem;margin-bottom:0.75rem}
.ab-testimonial-card blockquote{font-style:italic;margin-bottom:1rem;line-height:1.7}
.ab-testimonial-card__author strong{display:block}
.ab-testimonial-card__author span{font-size:0.875rem;color:var(--text-light)}

.ab-faq__item{padding:1rem 0;border-bottom:1px solid var(--border,#E2E8F0)}
.ab-faq__item summary{font-weight:600;cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center}
.ab-faq__item summary::after{content:'+';font-size:1.5rem;color:var(--primary)}
.ab-faq__item[open] summary::after{content:'−'}
.ab-faq__item p{margin-top:0.75rem;color:var(--text-light)}

.ab-form__field{margin-bottom:1rem}
.ab-form__field label{display:block;font-weight:500;margin-bottom:0.25rem}
.ab-form__field input,.ab-form__field textarea,.ab-form__field select{
  width:100%;padding:0.75rem;border:1px solid var(--border,#E2E8F0);
  border-radius:var(--radius-md,0.5rem);font-size:1rem;font-family:inherit}
.ab-form__field input:focus,.ab-form__field textarea:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px rgba(37,99,235,0.1)}
"""


# ─── Public API ─────────────────────────────────────────────────────────────

def render_block(block: dict) -> str:
    """Render a single content block to HTML."""
    block_type = block.get("type", "text")
    renderer = BLOCK_RENDERERS.get(block_type)
    if not renderer:
        return f"<!-- Unknown block type: {block_type} -->"
    return renderer(block)


def render_blocks(blocks: list) -> str:
    """Render multiple content blocks to HTML."""
    return "\n\n".join(render_block(b) for b in blocks)


def render_page_html(
    blocks: list,
    title: str = "Page",
    global_styles: Optional[dict] = None,
    seo_title: str = "",
    seo_description: str = "",
    og_image_url: str = "",
    canonical_url: str = "",
    custom_css: str = "",
    custom_js: str = "",
    head_code: str = "",
    body_start_code: str = "",
    body_end_code: str = "",
    google_fonts_url: str = "",
) -> str:
    """Render a complete HTML page from content blocks and site styling."""

    # Build CSS custom properties from global_styles
    css_vars = ""
    if global_styles:
        colors = global_styles.get("colors", {})
        for key, val in colors.items():
            css_vars += f"--{key.replace('_', '-')}:{val};"
        fonts = global_styles.get("fonts", {})
        if fonts.get("heading"):
            css_vars += f"--font-heading:'{fonts['heading']}',sans-serif;"
        if fonts.get("body"):
            css_vars += f"--font-body:'{fonts['body']}',sans-serif;"
        spacing = global_styles.get("spacing", {})
        for key, val in spacing.items():
            css_vars += f"--space-{key}:{val};"
        radii = global_styles.get("border_radius", {})
        for key, val in radii.items():
            css_vars += f"--radius-{key}:{val};"
        shadows = global_styles.get("shadows", {})
        for key, val in shadows.items():
            css_vars += f"--shadow-{key}:{val};"
        if global_styles.get("max_width"):
            css_vars += f"--max-width:{global_styles['max_width']};"
        if not google_fonts_url:
            google_fonts_url = global_styles.get("google_fonts_url", "")

    page_title = _esc(seo_title or title)
    meta_desc = _esc(seo_description)
    blocks_html = render_blocks(blocks)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{page_title}</title>
  {"<meta name='description' content='" + meta_desc + "' />" if meta_desc else ""}
  {"<link rel='canonical' href='" + _esc(canonical_url) + "' />" if canonical_url else ""}
  {"<meta property='og:title' content='" + page_title + "' />" if page_title else ""}
  {"<meta property='og:description' content='" + meta_desc + "' />" if meta_desc else ""}
  {"<meta property='og:image' content='" + _esc(og_image_url) + "' />" if og_image_url else ""}
  {"<link rel='stylesheet' href='" + _esc(google_fonts_url) + "' />" if google_fonts_url else ""}
  <style>
    :root{{{css_vars}}}
    {BASE_CSS}
    {COMPONENT_CSS}
    {custom_css}
  </style>
  {head_code}
</head>
<body>
  {body_start_code}
  <main>
    {blocks_html}
  </main>
  {body_end_code}
  {"<script>" + custom_js + "</script>" if custom_js else ""}
</body>
</html>"""
