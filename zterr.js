function main(item) {
    const url = item.url;
    const id = ku9.getQuery(url, "id");
    const playseek = ku9.getQuery(url, "playseek");
    if (!id) {
        return { url: url };
    }
    const base =
        "http://zterr.hvs.fj.chinamobile.com:6060/PLTV/88888888/224/"
        + id
        + "/index.m3u8";
    // ❗关键逻辑：判断是否回看
    if (!playseek || playseek.length < 10) {
        console.log("非法 playseek");
        return { url: base + "?servicetype=1" };
    }
    // 回看直接用 M3U 给的 playseek
    return {
        url: base + "?servicetype=3&playseek=" + playseek,
        player: 1,
        scale: 0,
        headers: {
            "User-Agent": "okhttp/3.12.11"
        }
    };
}

