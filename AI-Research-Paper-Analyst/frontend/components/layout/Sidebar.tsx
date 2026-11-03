"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  ["/dashboard", "Dashboard"], ["/papers", "Papers"], ["/chat", "Ask the papers"],
  ["/compare", "Compare"], ["/research-gaps", "Research gaps"], ["/literature-review", "Literature review"],
];

export default function Sidebar() {
  const path = usePathname();
  return (
    <nav className="bg-ink px-4 py-5 text-white md:min-h-screen md:w-56" aria-label="Main">
      <div className="mb-6 font-serif text-lg leading-tight">Research Paper<br />Analyst</div>
      <ul className="flex flex-wrap gap-1 md:block md:space-y-1">
        {links.map(([href, label]) => (
          <li key={href}>
            <Link href={href}
              className={`block rounded px-3 py-2 text-sm ${path.startsWith(href) ? "bg-white/15 font-medium" : "text-white/75 hover:bg-white/10"}`}>
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
