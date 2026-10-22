// Aplikasi menu bar clint: ikon + label di menu bar, panel web view (panel.html) saat diklik.
// Data diambil dari `python3 data.py` (JSON) setiap 2 detik; aksi dijalankan lewat scripts/clint-action.sh.
// Tidak memakai jaringan dan token. Dibangun dengan menubar/build.sh.
import Cocoa
import WebKit

let akar = Bundle.main.object(forInfoDictionaryKey: "ClintRoot") as? String
    ?? (NSHomeDirectory() + "/Desktop/clint")
let biru = NSColor(srgbRed: 106 / 255, green: 168 / 255, blue: 1, alpha: 1)

final class Panel: NSPanel {
    override var canBecomeKey: Bool { true }
}

final class App: NSObject, NSApplicationDelegate, WKScriptMessageHandler, WKNavigationDelegate {
    let item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
    var panel: Panel!
    var web: WKWebView!
    var data: [String: Any] = [:]
    var json = "{}"
    var avatar: NSImage?
    var detak = 0.0
    var animasi: Timer?
    var pemantau: Any?
    var sibuk = false

    func applicationDidFinishLaunching(_ n: Notification) {
        avatar = NSImage(contentsOfFile: NSHomeDirectory() + "/.config/clint/ikon.png")
        item.button?.target = self
        item.button?.action = #selector(klik)
        buatPanel()
        gambarLabel()
        segarkan()
        Timer.scheduledTimer(withTimeInterval: 2, repeats: true) { [weak self] _ in self?.segarkan() }
    }

    // ---- data ----
    func segarkan() {
        if sibuk { return }
        sibuk = true
        DispatchQueue.global().async {
            let p = Process()
            p.executableURL = URL(fileURLWithPath: "/usr/bin/env")
            p.arguments = ["python3", akar + "/menubar/data.py"]
            p.environment = ["PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin", "HOME": NSHomeDirectory()]
            let pipa = Pipe()
            p.standardOutput = pipa
            p.standardError = FileHandle.nullDevice
            try? p.run()
            let keluaran = pipa.fileHandleForReading.readDataToEndOfFile()
            p.waitUntilExit()
            DispatchQueue.main.async {
                self.sibuk = false
                guard let d = try? JSONSerialization.jsonObject(with: keluaran) as? [String: Any],
                      let teks = String(data: keluaran, encoding: .utf8) else { return }
                let berubah = teks != self.json
                self.data = d
                self.json = teks
                self.aturAnimasi()
                self.gambarLabel()
                if berubah && self.panel.isVisible { self.kirimKePanel() }
            }
        }
    }

    // ---- menu bar: avatar + label; saat bekerja bilah biru mengalir di bawah label ----
    var bekerja: Bool { (data["status"] as? String) == "bekerja" }

    func aturAnimasi() {
        if bekerja && animasi == nil {
            animasi = Timer.scheduledTimer(withTimeInterval: 1.0 / 30, repeats: true) { [weak self] _ in
                guard let self else { return }
                self.detak += 1.0 / 30
                self.gambarLabel()
            }
        } else if !bekerja, let t = animasi {
            t.invalidate()
            animasi = nil
        }
    }

    func gambarLabel() {
        guard let tombol = item.button else { return }
        let label = data["label"] as? String ?? ""
        let gelap = tombol.effectiveAppearance.bestMatch(from: [.darkAqua, .aqua]) == .darkAqua
        let warnaTeks: NSColor = gelap ? .white : .black
        let huruf = NSFont.systemFont(ofSize: bekerja ? 12 : 14, weight: .semibold)
        let atribut: [NSAttributedString.Key: Any] = [.font: huruf, .foregroundColor: warnaTeks]
        let ukuranTeks = (label as NSString).size(withAttributes: atribut)
        let lebarIsi = max(ukuranTeks.width, bekerja ? 44 : 0)
        // Pil setinggi menu bar (seperti tombol lain di menu bar): avatar 18 pt di kiri, label di kanannya.
        let tinggi: CGFloat = 22
        let lebar = label.isEmpty ? 26 : 2 + 18 + 7 + lebarIsi + 9
        let sp = bekerja ? 0.8 : 0.0
        let fase = sp > 0 ? (sin(detak / sp * .pi) + 1) / 2 : 0
        let gambar = NSImage(size: NSSize(width: lebar, height: tinggi), flipped: false) { _ in
            warnaTeks.withAlphaComponent(0.14).setFill()
            NSBezierPath(roundedRect: NSRect(x: 0, y: 0, width: lebar, height: tinggi), xRadius: 11, yRadius: 11).fill()
            let kotak = NSRect(x: label.isEmpty ? 4 : 2, y: 2, width: 18, height: 18)
            if let av = self.avatar {
                NSGraphicsContext.current?.saveGraphicsState()
                NSBezierPath(ovalIn: kotak).addClip()
                av.draw(in: kotak)
                NSGraphicsContext.current?.restoreGraphicsState()
            } else {
                NSColor(srgbRed: 74 / 255, green: 82 / 255, blue: 99 / 255, alpha: 1).setFill()
                NSBezierPath(ovalIn: kotak).fill()
            }
            guard !label.isEmpty else { return true }
            let x = 27.0
            if self.bekerja {
                (label as NSString).draw(at: NSPoint(x: x, y: 7), withAttributes: atribut)
                let rel = NSRect(x: x, y: 3.5, width: 44, height: 3)
                warnaTeks.withAlphaComponent(0.2).setFill()
                NSBezierPath(roundedRect: rel, xRadius: 1.5, yRadius: 1.5).fill()
                biru.setFill()
                let potong = NSRect(x: x + fase * 28, y: 3.5, width: 16, height: 3)
                NSBezierPath(roundedRect: potong, xRadius: 1.5, yRadius: 1.5).fill()
            } else {
                (label as NSString).draw(at: NSPoint(x: x, y: (tinggi - ukuranTeks.height) / 2), withAttributes: atribut)
            }
            return true
        }
        tombol.image = gambar
    }

    // ---- panel ----
    func buatPanel() {
        panel = Panel(contentRect: NSRect(x: 0, y: 0, width: 340, height: 300),
                      styleMask: [.borderless, .nonactivatingPanel], backing: .buffered, defer: false)
        panel.isFloatingPanel = true
        panel.level = .popUpMenu
        panel.backgroundColor = .clear
        panel.isOpaque = false
        panel.hasShadow = true
        panel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]

        let konfig = WKWebViewConfiguration()
        konfig.userContentController.add(self, name: "clint")
        web = WKWebView(frame: panel.contentRect(forFrameRect: panel.frame), configuration: konfig)
        web.setValue(false, forKey: "drawsBackground")
        web.wantsLayer = true
        web.layer?.cornerRadius = 12
        web.layer?.masksToBounds = true
        web.layer?.borderWidth = 1
        web.layer?.borderColor = NSColor(white: 1, alpha: 0.09).cgColor
        web.autoresizingMask = [.width, .height]
        web.navigationDelegate = self
        panel.contentView = web
        let html = URL(fileURLWithPath: akar + "/menubar/panel.html")
        web.loadFileURL(html, allowingReadAccessTo: html.deletingLastPathComponent())
    }

    @objc func klik() {
        panel.isVisible ? tutup() : bukaPanel()
    }

    func bukaPanel() {
        web.evaluateJavaScript("terbuka.clear()", completionHandler: nil)   // setiap dibuka, semua kartu tertutup
        kirimKePanel()
        letakkan(tinggi: panel.frame.height)
        panel.makeKeyAndOrderFront(nil)
        item.button?.highlight(true)
        pemantau = NSEvent.addGlobalMonitorForEvents(matching: [.leftMouseDown, .rightMouseDown]) { [weak self] _ in
            self?.tutup()
        }
    }

    func tutup() {
        panel.orderOut(nil)
        item.button?.highlight(false)
        if let p = pemantau { NSEvent.removeMonitor(p); pemantau = nil }
    }

    func letakkan(tinggi: CGFloat) {
        guard let jendela = item.button?.window else { return }
        let ikon = jendela.frame
        let layar = jendela.screen?.visibleFrame ?? NSScreen.main!.visibleFrame
        var x = ikon.maxX - 340
        x = min(max(x, layar.minX + 8), layar.maxX - 348)
        let tinggi = min(tinggi, ikon.minY - 6 - layar.minY - 8)   // daftar panjang: panel bisa digulir
        let y = ikon.minY - 6 - tinggi
        panel.setFrame(NSRect(x: x, y: y, width: 340, height: tinggi), display: true)
    }

    func kirimKePanel() {
        web.evaluateJavaScript("render(\(json))", completionHandler: nil)
    }

    func userContentController(_ c: WKUserContentController, didReceive pesan: WKScriptMessage) {
        guard let isi = pesan.body as? [String: Any] else { return }
        if let t = isi["tinggi"] as? Double, t > 0 {
            if panel.isVisible { letakkan(tinggi: t) } else { panel.setContentSize(NSSize(width: 340, height: t)) }
        }
        if let args = isi["aksi"] as? [String] {
            jalankan(args)
            if (isi["tetap"] as? Bool) != true { tutup() }
        }
    }

    func jalankan(_ args: [String]) {
        let p = Process()
        p.executableURL = URL(fileURLWithPath: "/bin/bash")
        p.arguments = [akar + "/scripts/clint-action.sh"] + args
        p.environment = ["PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin", "HOME": NSHomeDirectory()]
        p.terminationHandler = { _ in DispatchQueue.main.async { self.segarkan() } }
        try? p.run()
    }

    func webView(_ w: WKWebView, didFinish n: WKNavigation!) { kirimKePanel() }
}

let app = NSApplication.shared
let delegasi = App()
app.delegate = delegasi
app.setActivationPolicy(.accessory)
app.run()
