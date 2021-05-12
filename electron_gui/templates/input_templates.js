module.exports = {

    datalist: function (name, options, defaultValue) {
        let datalistHtmlString =
            `<div class="input-group input-group-sm mb-3 w-auto vojp_text">\n` +
            `<label class="input-group-text vojp_input_label" for="${name}">${name}</label>\n` +
            `<select class="form-select vojp_input" id="${name}">\n` +
            `<option selected>${defaultValue}</option>\n`
        if (typeof options === 'object') {
            Object.entries(options).forEach(optionKeyValuePair => {
                datalistHtmlString += `<option value="${optionKeyValuePair[0]}">${optionKeyValuePair[1]}</option>`
            })
        } else {
            options.forEach(option => {
                datalistHtmlString += `<option value="${option}">${option}</option>`
            })
        }

        datalistHtmlString += '</datalist></div>'
        return datalistHtmlString
    },

    textInput: function (name, defaultValue) {
        return `<div class="input-group input-group-sm mb-3">` +
            `<span class="input-group-text vojp_input_label" id ="inputGroup-sizing-sm">${name}</span>` +
            `<input type="text" class="form-control vojp_input" placeholder="${defaultValue}" aria-label="${name}" aria-describedby="inputGroup-sizing-sm">` +
            `</div>`
    },

    checkboxInput: function (name, defaultValue) {
        return `<div class="form-check form-switch">` +
            `<input class="form-check-input vojp_switch" type="checkbox" value="${defaultValue}" id="${name}">` +
            `<label class="form-check-label vojp_input_label" for="${name}">${name}</label></div>`
    }
}
