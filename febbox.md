# Extractor function for febbox(showbox) - tmdb based.

- id : tmdb id
- s : season number(0 for movies)
- e : episode numbers(0 for movies)

### Function
```js
const streams = await extractor(INT,INT,INT);
```

### Code
```js
// get the season and episode number from filename.
function getSeasonEpisode(text) {
  const pattern = /s(\d{1,3})e(\d{1,4})/i;
  const match = text.match(pattern);
  if (match) {
    const season = parseInt(match[1], 10);
    const episode = parseInt(match[2], 10);
    return {
      season,
      episode
    };
  } else {
    return null;
  }
}
async function extractor(id, s = 0, e = 0) {
  const data = {
    id: id,
    type: "",
    s: s,
    e: e
  }

  // build base api url.
  let _tv = ''
  if (data.s !== 0 || data.e !== 0) {
    data.type = "S";
    _tv = `.${s}.1`; // setting ep 1 cuz most ep dosent have id
  } else {
    data.type = "M";
  }

  // 2. get showbox-id from api(dmdb)
  const idApiRequest = await fetch(`https://api.dmdb.network/v1/gmid/${data.type}.${data.id}${_tv}`);
  const idApiJson = await idApiRequest.json()
  if (idApiRequest.status === 404 || idApiJson['ids'].length === 0) {
    return []
  }

  // 2. get febbox-id 
  const mode = data.type === "M" ? 1 : 2;
  const sheguId = idApiJson['ids']['superstream'];
  console.log(`http://showbox.shegu.net/index/share_link?id=${sheguId}&type=${mode}`)
  const febboxIdRequest = await fetch(`http://showbox.shegu.net/index/share_link?id=${sheguId}&type=${mode}`);
  const febboxIdJson = await febboxIdRequest.json()
  const febboxIdLink = febboxIdJson['data']['link']

  // 3. get base file details.
  const febboxId = febboxIdLink.split("/")[febboxIdLink.split("/").length - 1]
  const febboxItemRequest = await fetch(`https://www.febbox.com/file/file_share_list?share_key=&{febboxId}`);
  const febboxItemJson = await febboxItemRequest.json()

  // 4. fetch the movie or series
  let febboxItemId;
  let server;
  if (data.type === "M") {
    if (server > febboxItemJson['data']['file_list'].length) {
      server = (febboxItemJson['data']['file_list'].length - 1); // chose any of the listed servers for movies.
    }
    febboxItemId = febboxItemJson['data']['file_list'][server]['fid']
  } else {
    // this is a custom code written to get episodes in seasons in a series.
    for (const [i, item] of febboxItemJson['data']['file_list'].entries()) {
      if (item.file_icon === "dir_icon" && item.file_name.includes("eason")) {
        let _temp = item.file_name.split(" ");
        let season = _temp[_temp.length - 1];
        if (Number(data.s) === Number(season)) {
          // check the maximum pagination.
          const febboxSeasonId = item.fid;
          const apiReq = await fetch(`https://www.febbox.com/file/file_share_list?page=1&share_key=${febboxId}&pwd=&parent_id=${febboxSeasonId}`);
          const apiResp = await apiReq.json()
          let _largest = 1
          for (const x of apiResp.data.file_list) {
            const _data = getSeasonEpisode(x.file_name)
            if (_data.episode > _largest) {
              _largest = _data.episode;
            }
          }
          const totalSections = Math.ceil(_largest / 30) + 1

          _temp = await fetch(`https://www.febbox.com/file/file_share_list?page=${totalSections}&share_key=${febboxId}&pwd=&parent_id=${febboxSeasonId}`);
          let _tempr = await _temp.json()
          const late = _tempr.data.file_list.length;
          const psections = (_largest - late) - 1;
          const ne = Number(data.e);
          const sec_ne = Math.ceil(ne / 30);
          const predictedPages = [totalSections - sec_ne, (totalSections - sec_ne) - 1, (totalSections - sec_ne) + 1] // predict the pages where the specific ep should be.
          let page_search = true;
          let episodedReq;
          let episodedResp;
          let episodeList = [];
          let page = 0;
          console.log(predictedPages)
          while (page_search) {
            if (page < (predictedPages.length)) {
              episodedReq = await fetch(`https://www.febbox.com/file/file_share_list?page=${predictedPages[page]}&share_key=${febboxId}&pwd=&parent_id=${febboxSeasonId}`);
              episodedResp = await episodedReq.json();

              if (episodedResp['data']['file_list'].length === 0) {
                page_search = false;
              } else {
                episodeList.push(...episodedResp['data']['file_list'])
                page = page + 1;
              }
            } else {
              break
            }
          }
          for (const ep of episodeList) {
            if (ep.file_icon === 'video_icon') {
              if (ep.file_name.includes(`s${data.s.toString().padStart(2, '0')}e${data.e.toString().padStart(2, '0')}`) || ep.file_name.includes(`S${data.s.toString().padStart(2, '0')}E${data.e.toString().padStart(2, '0')}`)) {
                console.log(ep.file_icon, ep.file_name);
                febboxItemId = ep.fid;
                break
              }
            }
          }
        }
      }
    }

  }
  console.log(febboxItemId)
  const post_data = `fid=${febboxItemId}&share_key=${febboxId}`
  const urlRequest = await fetch(`https://www.febbox.com/file/player`, {
    body: post_data,
    method: 'POST'
  })
  const urlResponse = await urlRequest.text()
  const regex = /\{"type":(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}/g;
  const matches = urlResponse.match(regex);
  const responseData = []
  if (matches) {
    matches.forEach(match => {
      try {
        const jsonObject = JSON.parse(match);
        responseData.push(jsonObject);
      } catch (error) {
        console.error('Error', match, error);
      }
    });
  }
  return responseData;
}
```
