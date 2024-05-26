async function renderDataTable() {
  const dataUrl =
    // "https://raw.githubusercontent.com/AOSC-Dev/anicca/main/pkgsupdate.json";
    "anicca-data.json"

  const data = await fetch(dataUrl).then((response) => response.json());

  const dataSet = data.map((row) => {
    row[1] = row[1].replaceAll("+", "<br>+");
    row[4] = (new Date(row[4]*1000)).toLocaleDateString()
    return Object.values(row);
  });

  const table = new DataTable("#pkgsupdate", {
    columns: [
      { title: "Package" },
      { title: "Repo Version" },
      { title: "New Version" },
      { title: "Category" },
      { title: "Repo Date"},
      { title: "Warnings" },
    ],
    scrollX: true,
    lengthMenu: [
      10,
      25,
      50,
      100,
      { label: "8d", value: 0x8d },
      { label: "All", value: -1 },
    ],
    search: {
      regex: true,
    },
    layout: {
      bottomEnd: {
        paging: {
          type: "simple_numbers",
        },
      },
    },
    data: dataSet,
  });

  table.page.len(25).draw();
}

async function getUpdateDate() {
  const dataUrl = "https://api.github.com/repos/AOSC-Dev/anicca/branches/main";
  const data = await fetch(dataUrl).then((response) => response.json());
  const updateTimestamp = Date.parse(data.commit.commit.author.date);

  const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
  document.getElementById("update-time").innerText =
    "Updated " +
    rtf.format(parseInt((updateTimestamp - Date.now()) / 60000), "minute");
}

renderDataTable();
getUpdateDate();
