// dataset fields
var carFields = {
  categ: ["Cylinders", "Name", "Origin"],
  date: ["Year"],
  quant: [
    "Acceleration",
    "Displacement",
    "Horsepower",
    "Miles_per_Gallon",
    "Weight_in_lbs",
  ],
};

// global vars
var bookmarkContent = document.querySelector(".bookmark_content");
var taskContent = document.querySelector(".task_content");
var gstdyContent = document.querySelector(".gstdy_content");
var fieldLst = document.querySelector(".attr-lst");

var mainImg = document.querySelector(".mainImg");
var relatedImg = document.querySelector(".relatedImg");

var rec = [];
var curRecLen = 0;

var checkedFields = [];
var propVglMap = {};
var propVglstrMap = {};
var bookmarked = {};

//save cur answer
var curAns = "";

var hrefSplit = window.location.href.split("/");
var hrefSplitLen = hrefSplit.length;
var status = hrefSplit[hrefSplitLen - 2];

var interactionLogs = [];
var scrollPos;

init();

function init() {
  initFields();
  initBtns();
  generateInitRecPlots();
  storeInteractionLogs("study begins (demo)", "page loaded", new Date());
  scrollPos = document.querySelector(".page_content").scrollTop;

  // adding scroll event
  document
    .querySelector(".page_content")
    .addEventListener("scroll", function () {
      // detects new state and compares it with the new one
      // console.log(scrollPos, document.querySelector(".page_content").scrollTop);
      if (document.querySelector(".page_content").scrollTop > scrollPos) {
        // console.log("scroll up.");
        storeInteractionLogs("scroll down", "", new Date());
      } else {
        // console.log("scroll down.");
        storeInteractionLogs("scroll up", "", new Date());
      }
      // saves the new position for iteration.
      scrollPos = document.querySelector(".page_content").scrollTop;
    });
}

function initBtns() {
  // popup windows
  let bmModal = document.querySelector("#bmpopup");
  let bmBtn = document.querySelector("#bookmark");
  let bmClose = document.querySelector("#bmclose");

  let tskModal = document.querySelector("#tskpopup");
  let tskBtn = document.querySelector("#task");
  let tskClose = document.querySelector("#tskclose");

  let gstdyModal = document.querySelector("#gstdypopup");
  let gstdyBtn = document.querySelector("#go_study");
  let gstdyClose = document.querySelector("#gstdyclose");

  bmBtn.addEventListener("click", () => {
    if (bmModal.style.display == "block") {
      bmModal.style.display = "none";
      storeInteractionLogs("closed window", "bookmark popup", new Date());
    } else {
      bmModal.style.display = "block";
      refreshBookmark();
      storeInteractionLogs("opened window", "bookmark popup", new Date());
    }
  });

  bmClose.addEventListener("click", () => {
    bmModal.style.display = "none";
    storeInteractionLogs("closed window", "bookmark popup", new Date());
  });

  tskBtn.addEventListener("click", () => {
    if (tskModal.style.display == "block") {
      tskModal.style.display = "none";
      storeInteractionLogs("closed window", "task popup", new Date());
      let tskId = "t-answer";
      curAns = document.getElementById(tskId).value;
    } else {
      tskModal.style.display = "block";
      storeInteractionLogs("opened window", "task popup", new Date());
      displayTask();
      let tskId = "t-answer";
      document.getElementById(tskId).value = curAns;
    }
  });

  tskClose.addEventListener("click", () => {
    tskModal.style.display = "none";
    storeInteractionLogs("closed window", "task popup", new Date());
    let tskId = "t-answer";
    curAns = document.getElementById(tskId).value;
  });

  gstdyBtn.addEventListener("click", () => {
    if (gstdyModal.style.display == "block") {
      gstdyModal.style.display = "none";
      storeInteractionLogs("closed window", "go study popup", new Date());
    } else {
      gstdyModal.style.display = "block";
      storeInteractionLogs("opened window", "go study popup", new Date());
      displayGstdy();
    }
  });

  gstdyClose.addEventListener("click", () => {
    gstdyModal.style.display = "none";
    storeInteractionLogs("closed window", "go study popup", new Date());
  });

  window.addEventListener("click", (event) => {
    if (event.target == bmModal) {
      bmModal.style.display = "none";
      storeInteractionLogs("closed window", "task popup", new Date());
    }
    if (event.target == tskModal) {
      tskModal.style.display = "none";
      storeInteractionLogs("closed window", "task popup", new Date());
      let tskId = "t-answer";
      curAns = document.getElementById(tskId).value;
    }
    if (event.target == gstdyModal) {
      gstdyModal.style.display = "none";
      storeInteractionLogs("closed window", "task popup", new Date());
    }
  });
}

function initFields() {
  let fields = carFields;
  fieldLst.innerHTML = "";
  let res = "";
  for (e of fields.categ) {
    res += `<li class="categ-attr enabled">
                      <div>
                          <i class="fas fa-font"></i> &nbsp;
                          <label class="form-check-label" for="${e}">
                             ${e}
                          </label>
                          <span class="check float-right">
                              <input class="form-check-input" type="checkbox" value="${e}" id="${e}"/>
                          </span>
                      </div>
                  </li>`;
  }
  for (e of fields.date) {
    res += `<li class="date-attr enabled">
                      <div>
                          <i class="fas fa-calendar-alt"></i> &nbsp;
                          <label class="form-check-label" for="${e}"> ${e} </label>
                          <span class="check float-right">
                              <input class="form-check-input" type="checkbox" value="${e}" id="${e}" />
                          </span>
                      </div>
                  </li>`;
  }
  for (e of fields.quant) {
    res += `<li class="quant-attr enabled">
                      <div>
                          <i class="fas fa-hashtag"></i> &nbsp;
                          <label class="form-check-label" for="${e}"> ${e} </label>
                          <span class="check float-right">
                              <input class="form-check-input" type="checkbox" value="${e}" id="${e}" />
                          </span>
                      </div>
                  </li>`;
  }
  fieldLst.innerHTML += res;
  // click on fields
  let fldCheckboxes = document.querySelectorAll("form .enabled div");
  for (fldcb of fldCheckboxes) {
    fldcb.addEventListener("click", clickOnField);
  }
}

function clickOnField(e) {
  console.log(checkedFields);
  let box = e.target;
  if (box != null) {
    let clickedField = box.value;
    // if a box is checked after the click
    if (box.checked) {
      // if we can check more fields add the field in.
      // also add its parsed name to the list.
      if (checkedFields.length < 3) {
        checkedFields.push(clickedField);
        storeInteractionLogs(
          "clicked on a field",
          "add " + clickedField,
          new Date()
        );
        // if we can not check more fields, alert it.
      } else {
        storeInteractionLogs(
          "clicked on a field",
          "tried to add " +
            clickedField +
            ", but failed because already selected 3 fields",
          new Date()
        );
        alert(`You have selected more than 3 fields!`);
        box.checked = false;
        return;
      }

      // if a box is unchecked after the click,
      // also remove its parsed name from the list.
    } else {
      storeInteractionLogs(
        "clicked on a field",
        "removed " + clickedField,
        new Date()
      );
      checkedFields = checkedFields.filter(function (value, index, arr) {
        return value.localeCompare(clickedField) != 0;
      });
      // if 0 fields are checked, display alternative message.
      if (checkedFields.length == 0) {
        generateInitRecPlots();
        return;
      }
    }
    generatePlot(clickedField, box);
  }
}

function generateInitRecPlots() {
  var data = {
    data: JSON.stringify({
      fields: [],
    }),
  };
  $.ajax({
    async: false,
    type: "POST",
    url: "/demo_snd_flds",
    currentType: "application/json",
    data: data,
    dataType: "json",
    success: function (response) {
      console.log(response);
      mainImg.innerHTML = `No specified visualization yet. Start exploring by selecting fields on the Field panel or specifying a chart below.`;
      relatedImg.innerHTML = "";
      rec = response.recVegalite;
      for (var i = 0; i < rec.length; i++) {
        for (let prop in rec[i]) {
          let prop_str = JSON.stringify(prop).replace(/\W/g, "");
          let vglSpec = rec[i][prop];
          let sFlds = getFieldsFromVgl(vglSpec);
          let added_str = "";
          for (let fld of sFlds) {
            if (carFields.categ.includes(fld)) {
              added_str += `<i class="fas fa-font show_fld"> ${fld} </i>`;
            }
            if (carFields.quant.includes(fld)) {
              added_str += `<i class="fas fa-hashtag show_fld"> ${fld} </i>`;
            }
            if (carFields.date.includes(fld)) {
              added_str += `<i class="fas fa-calendar-alt show_fld"> ${fld} </i>`;
            }
            console.log(added_str);
          }
          relatedImg.innerHTML += `<div class='view_wrapper ${prop_str}_wrapper'> ${added_str} <i class='fas fa-bookmark add_bm' added="false"></i><i class="fas fa-list-alt specify_chart"></i><div class="views" id='${prop_str}'></div></div>`;

          vegaEmbed(`#${prop_str}`, vglSpec);
          propVglMap[prop_str] = vglSpec;
          propVglstrMap[prop_str] = prop;
        }
      }
      document.querySelector(".loadmoreDiv").style.display = "none";
      addChartBtnsListener();
      addChartsListener();
    },
  });
}

function generatePlot(clickedField, box) {
  console.log(checkedFields);
  var data = {
    data: JSON.stringify({
      fields: checkedFields,
    }),
  };
  $.ajax({
    async: false,
    type: "POST",
    url: "/demo_snd_flds",
    currentType: "application/json",
    data: data,
    dataType: "json",
    success: function (response) {
      if (response.status === "success") {
        console.log(response);
        var vglDict = response.actualVegalite;
        rec = response.recVegalite;
        for (let prop in vglDict) {
          prop_str = prop.replace(/\W/g, "");
          let added_str = "";
          checkedFields.sort();
          for (let fld of checkedFields) {
            if (carFields.categ.includes(fld)) {
              added_str += `<i class="fas fa-font show_fld"> ${fld} </i>`;
            }
            if (carFields.quant.includes(fld)) {
              added_str += `<i class="fas fa-hashtag show_fld"> ${fld} </i>`;
            }
            if (carFields.date.includes(fld)) {
              added_str += `<i class="fas fa-calendar-alt show_fld"> ${fld} </i>`;
            }
            console.log(added_str);
          }
          mainImg.innerHTML = `<div id="main_wrapper" class="view_wrapper ${prop_str}_wrapper"> ${added_str} <i class="fas fa-bookmark add_bm" added="false"></i><div class="views ${prop_str}" id="main"></div></div>`;
          let vglSpec = vglDict[prop];
          vegaEmbed("#main", vglSpec);
          propVglMap[prop_str] = vglSpec;
          propVglstrMap[prop_str] = prop;
          storeInteractionLogs(
            "main chart changed because of clicking a field",
            prop,
            new Date()
          );
        }
        generateRecPlots();
      } else if (response.status === "empty") {
        storeInteractionLogs(
          "triggered empty chart",
          "removed " + clickedField,
          new Date()
        );
        // if empty chart
        alert(
          "Sorry, we cannot generate charts with the combination of selected fields."
        );
        checkedFields = checkedFields.filter(function (value, index, arr) {
          return value.localeCompare(clickedField) != 0;
        });
        box.checked = false;
        console.log(checkedFields);
      }
    },
  });
}

function generateRecPlots() {
  relatedImg.innerHTML = "";
  document.querySelector(".loadmoreDiv").style.display = "none";
  console.log(rec);
  let maxNum = 5;
  if (maxNum > rec.length) {
    maxNum = rec.length;
  }
  for (var i = 0; i < rec.length; i++) {
    for (let prop in rec[i]) {
      let prop_str = JSON.stringify(prop).replace(/\W/g, "");

      let vglSpec = rec[i][prop];
      vegaEmbed(`#${prop_str}`, vglSpec);
      let sFields = getFieldsFromVgl(vglSpec);
      // console.log(sFields);
      let added_str = "";
      for (let fld of sFields) {
        if (carFields.categ.includes(fld)) {
          added_str += `<i class="fas fa-font show_fld"> ${fld} </i>`;
        }
        if (carFields.quant.includes(fld)) {
          added_str += `<i class="fas fa-hashtag show_fld"> ${fld} </i>`;
        }
        if (carFields.date.includes(fld)) {
          added_str += `<i class="fas fa-calendar-alt show_fld"> ${fld} </i>`;
        }
      }

      relatedImg.innerHTML += `<div class='view_wrapper ${prop_str}_wrapper'> ${added_str} <i class='fas fa-bookmark add_bm' added="false"></i><i class="fas fa-list-alt specify_chart"></i><div class="views" id='${prop_str}'></div></div>`;

      propVglMap[prop_str] = vglSpec;
      propVglstrMap[prop_str] = prop;
      if (i >= maxNum) {
        document.querySelector(`.${prop_str}_wrapper`).style.display = "none";
      }
    }
  }
  addChartBtnsListener();
  addChartsListener();

  if (rec.length > 5) {
    curRecLen = 5;
    document.querySelector(".loadmoreDiv").style.display = "block";
    document
      .querySelector("#loadmoreBtn")
      .addEventListener("click", loadMoreRec);
  }
}

function loadMoreRec() {
  storeInteractionLogs("clicked load more button", "", new Date());
  let maxNum = curRecLen + 5;
  if (maxNum >= rec.length) {
    maxNum = rec.length;
    document.querySelector(".loadmoreDiv").style.display = "none";
  }
  for (var i = curRecLen; i < maxNum; i++) {
    for (let prop in rec[i]) {
      let prop_str = JSON.stringify(prop).replace(/\W/g, "");
      document.querySelector(`.${prop_str}_wrapper`).style.display = "block";
    }
  }
  // addChartBtnsListener();
  curRecLen = maxNum;
}

function specifyChart(e) {
  let vis = e.target.parentElement;
  let prop_str = vis.classList.item(1).split("_wrapper")[0];
  let vglSpec = propVglMap[prop_str];

  storeInteractionLogs("specified chart", propVglstrMap[prop_str], new Date());

  reassignFields(vglSpec);

  var data = {
    data: JSON.stringify({
      vgl: vglSpec,
    }),
  };
  $.ajax({
    async: false,
    type: "POST",
    url: "/demo_snd_spcs",
    currentType: "application/json",
    data: data,
    dataType: "json",
    success: function (response) {
      console.log(response);
      rec = response.recVegalite;

      let sFields = getFieldsFromVgl(vglSpec);
      console.log(sFields);
      let added_str = "";
      for (let fld of sFields) {
        if (carFields.categ.includes(fld)) {
          added_str += `<i class="fas fa-font show_fld"> ${fld} </i>`;
        }
        if (carFields.quant.includes(fld)) {
          added_str += `<i class="fas fa-hashtag show_fld"> ${fld} </i>`;
        }
        if (carFields.date.includes(fld)) {
          added_str += `<i class="fas fa-calendar-alt show_fld"> ${fld} </i>`;
        }
      }

      mainImg.innerHTML = `<div id="main_wrapper" class="view_wrapper ${prop_str}_wrapper"> ${added_str} <i class="fas fa-bookmark add_bm" added="false"></i><div class="views ${prop_str}" id="main"></div></div>`;

      vegaEmbed("#main", vglSpec);
      generateRecPlots();
    },
  });
}

function reassignFields(vgljson) {
  console.log(vgljson);
  let all_boxes = document.querySelectorAll(".form-check-input");
  console.log(all_boxes);

  let fields = getFieldsFromVgl(vgljson);

  for (box of all_boxes) {
    // console.log(box.value);
    if (fields.includes(box.value)) {
      box.checked = true;
    } else {
      box.checked = false;
    }
  }
  checkedFields = fields;
}

function addChartBtnsListener() {
  // add event listeners to all bookmark buttons on the page
  let btns = document.querySelectorAll(".add_bm");
  for (btn of btns) {
    btn.addEventListener("click", toggleBookMark);
  }

  let specBtns = document.querySelectorAll(".specify_chart");
  for (sBtn of specBtns) {
    sBtn.addEventListener("click", specifyChart);
  }

  let wrappers = document.querySelectorAll(".view_wrapper");

  // change color and state of a bookmark if a wrapper is in the bookmark content.
  for (wrapper of wrappers) {
    let item = `${wrapper.classList.item(1).split("_wrapper")[0]}`;
    if (item in bookmarked) {
      wrapper.querySelector(".add_bm").style.color = "#ffa500";
      wrapper.querySelector(".add_bm").setAttribute("added", "true");
    }
  }
}

function toggleBookMark(e) {
  let btn = e.target;
  let vis = e.target.parentElement;
  let str = vis.classList.item(1);
  // if the mark was checked, user want to uncheck it.
  if (btn.getAttribute("added") == "true") {
    // remove bookmark from pop up window
    let arr = bookmarkContent.childNodes;
    for (n of arr) {
      if (
        `${str}`
          .split("_wrapper")[0]
          .split("_bm")[0]
          .localeCompare(n.classList.item(1).split("_bm")[0]) == 0
      ) {
        bookmarkContent.removeChild(n);
      }
    }
    let splittedStr = `${str.split("_wrapper")[0]}`;
    delete bookmarked[splittedStr];
    storeInteractionLogs(
      "deleted chart from bookmark",
      propVglstrMap[splittedStr],
      new Date()
    );

    // change color and state of the plot in views
    let mark = document.querySelector(`.${str.split("_bm")[0]} .add_bm`);
    if (mark != null) {
      mark.style.color = "rgb(216, 212, 223)";
      mark.setAttribute("added", "false");
    }
    refreshBookmark();

    // if the mark is unchecked, user want to check it.
  } else {
    btn.style.color = "#ffa500";
    btn.setAttribute("added", "true");

    let splittedStr = `${str.split("_wrapper")[0]}`;

    bookmarked[splittedStr] = propVglMap[splittedStr];

    storeInteractionLogs(
      "added chart to bookmark",
      propVglstrMap[splittedStr],
      new Date()
    );
    refreshBookmark();
  }
}

function refreshBookmark() {
  let btnstrs = [];

  if (Object.keys(bookmarked).length == 0) {
    bookmarkContent.innerHTML =
      "Oops, you don't have any bookmark yet. Click on bookmark tags on charts to add a bookmark!";
  } else {
    bookmarkContent.innerHTML = "";
    for (key of Object.keys(bookmarked)) {
      let value = bookmarked[key];
      console.log(bookmarked);
      console.log(key);

      let sFields = getFieldsFromVgl(propVglMap[key]);
      console.log(sFields);
      let added_str = "";
      for (let fld of sFields) {
        if (carFields.categ.includes(fld)) {
          added_str += `<i class="fas fa-font show_fld"> ${fld} </i>`;
        }
        if (carFields.quant.includes(fld)) {
          added_str += `<i class="fas fa-hashtag show_fld"> ${fld} </i>`;
        }
        if (carFields.date.includes(fld)) {
          added_str += `<i class="fas fa-calendar-alt show_fld"> ${fld} </i>`;
        }
      }

      // creat div structure append to the popup window.
      bookmarkContent.innerHTML += `<div class="view_wrapper ${key}_wrapper_bm" > ${added_str} <i class="fas fa-bookmark add_bm" added="true"></i><div class="views" id="${key}_bm"></div></div>`;

      // plot the recommandation
      vegaEmbed(`#${key}_bm`, value);

      btnstrs.push(`.${key}_wrapper_bm .add_bm`);
      let btn = document.querySelector(`.${key}_wrapper_bm .add_bm`);

      // change color and attribute of bookmark.
      btn.style.color = "#ffa500";
      btn.setAttribute("added", "true");
    }
    // add event listener to new bookmark
    for (btn of btnstrs)
      document.querySelector(btn).addEventListener("click", toggleBookMark);
  }
}

function displayTask() {
  taskContent.innerHTML =
    "<div><b>Question:</b> The current question would be described here. <br> Example: Which origin has the most number of records? <br><br><label>Your answer:</label> &nbsp;&nbsp; <input type='text' id='t-answer'><br><input type='checkbox' id='t-complete-bm' /> &nbsp;&nbsp; <label>I have also bookmarked the charts which I think they could answer the quesion.</label><br><a class='btn btn-outline-dark' href='#' role='button'>Submit, then go to next step.</a></div>";

  let ansId = "t-answer";
  document.getElementById(ansId).addEventListener("input", function () {
    storeInteractionLogs(
      "typed in answer",
      document.getElementById(ansId).value,
      new Date()
    );
  });
}

function displayGstdy() {
  if (status === "pilot") {
    gstdyContent.innerHTML =
      "<div>Please pick a <b>username</b>:  (The username is only for logging. The username can <b>only</b> consists of <b>alphabets</b> or <b>numbers</b>.) <br> <label for='username'>Username:</label>&nbsp; <input type='text' id='username'><br><br> <button type='button' class='btn btn-sm btn-outline-info' onclick='goStudy()'><i class='fa fa-sign-in'></i> &nbsp; Go to Study</button></div>";
  } else if (status === "study") {
    gstdyContent.innerHTML =
      "<div>Please enter the <b>email address</b> you used for the study registration: <br> <label for='username'>Email:</label>&nbsp; <input type='text' id='username'><br><br> <button type='button' class='btn btn-sm btn-outline-info' onclick='goStudy()'><i class='fa fa-sign-in'></i> &nbsp; Go to Study</button></div>";
  }
  let unameId = "username";
  document.getElementById(unameId).addEventListener("input", function () {
    storeInteractionLogs(
      "typed in username/email address",
      document.getElementById(unameId).value,
      new Date()
    );
  });
}

function goStudy() {
  storeInteractionLogs("hit the go study button", "", new Date());
  let inputText = document.getElementById("username").value;
  const regex = /[a-zA-Z\d]+/g;

  if (inputText === "") {
    alert("Please input a username.");
    storeInteractionLogs(
      "submission failed",
      "did not enter username/email address",
      new Date()
    );
    return;
  }
  if (status === "pilot") {
    let mat = inputText.match(regex);
    if (mat.length == 1 && mat[0].length == inputText.length) {
      sendUserInfo(inputText, status);
    } else {
      alert(
        "Please input a valid username. (The username can only consists of alphabets or numbers.)"
      );
      storeInteractionLogs("submission failed", "invalid username", new Date());
    }
  } else if (status === "study") {
    sendUserInfo(inputText, status);
  }
}

function sendUserInfo(username, status) {
  var data = {
    data: JSON.stringify({
      username: username,
      status: status,
    }),
  };
  $.ajax({
    async: false,
    type: "POST",
    url: "/snd_user_info",
    currentType: "application/json",
    data: data,
    dataType: "json",
    success: function (response) {
      if (response.status === "success") {
        let username = response.username;
        let version = response.version;
        storeInteractionLogs("submitted successfully", "", new Date());
        var log = {
          log: JSON.stringify({
            interactionLogs: interactionLogs,
            status: version,
            username: username,
            interface: "demo",
            bookmarked: bookmarked,
          }),
        };
        $.ajax({
          async: false,
          type: "POST",
          url: "/snd_demo_interaction_logs",
          currentType: "application/json",
          data: log,
          dataType: "json",
          success: function (response) {
            console.log(response);
          },
        });
        if (version === "pilot") {
          window.location = "/pilot/" + username + "/ace/t2";
        } else {
          window.location = "/study/" + username + "/" + version + "/t1";
        }
      } else if (response.status === "invalid") {
        if (status === "pilot") {
          alert("Sorry, the username has been taken. Please try another one.");
          storeInteractionLogs(
            "submission failed",
            "username is taken",
            new Date()
          );
        } else {
          alert(
            "The email address has not been registered for the user study."
          );
          storeInteractionLogs(
            "submission failed",
            "the email address has not been registered",
            new Date()
          );
        }
      }
    },
  });
}

function addChartsListener() {
  allCharts = document.getElementsByClassName("views");
  // console.log(allCharts);
  for (let chart of allCharts) {
    // console.log(chart);
    chart.addEventListener("scroll", () => {
      storeInteractionLogs(
        "scroll on a chart",
        propVglstrMap[chart.id],
        new Date()
      );
    });
    chart.addEventListener("mouseover", () => {
      storeInteractionLogs(
        "mouseover a chart",
        propVglstrMap[chart.id],
        new Date()
      );
    });
    chart.addEventListener("mouseout", () => {
      storeInteractionLogs(
        "mouseout a chart",
        propVglstrMap[chart.id],
        new Date()
      );
    });
  }
}

function storeInteractionLogs(interaction, value, time) {
  console.log({ Interaction: interaction, Value: value, Time: time.getTime() });
  interactionLogs.push({
    Interaction: interaction,
    Value: value,
    Time: time.getTime(),
  });
}

function getFieldsFromVgl(vgl) {
  var flds = [];
  for (encode in vgl["encoding"]) {
    if ("field" in vgl["encoding"][encode]) {
      flds.push(vgl["encoding"][encode]["field"]);
    }
  }
  flds.sort();
  return flds;
}
