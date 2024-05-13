async function renderDataTable() {
  const dataUrl =
    "https://raw.githubusercontent.com/Suyun114/anicca-aosc/main/pkgsupdate.json";

  const data = await fetch(dataUrl).then((response) => response.json());

  const dataSet = data.map((row) => {
    row.before = row.before.replaceAll("+", "<br>+");
    row.path = row.path.slice(0, row.path.lastIndexOf("/"));
    return Object.values(row);
  });

  new DataTable("#pkgsupdate", {
    columns: [
      { title: "Package" },
      { title: "Repo Version" },
      { title: "New Version" },
      { title: "Category" },
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
}

async function getUpdateDate() {
  const dataUrl =
    "https://api.github.com/repos/AOSC-Dev/anicca/branches/main";
  const data = await fetch(dataUrl).then((response) => response.json());
  const updateTimestamp = Date.parse(data.commit.commit.author.date);

  const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
  document.getElementById("update-time").innerText =
    "Updated " +
    rtf.format(parseInt((updateTimestamp - Date.now()) / 60000), "minute");
}

renderDataTable();
getUpdateDate();
