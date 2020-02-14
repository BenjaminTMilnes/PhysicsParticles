
class ScientificNumber {
    constructor(number) {
        this._decimal = new Decimal(number);
    }

    get isPositive() {
        return this._decimal.gt(0);
    }

    get isNegative() {
        return this._decimal.lt(0);
    }

    get orderOfMagnitude() {
        return this._decimal.log10().floor();
    }

    get significand() {
        var o = - this.orderOfMagnitude;

        return this._decimal.times((new Decimal(10)).pow(o));
    }

    toHTML(precision = 3, includePlusSign = true) {
        var sign = "";

        if (this.isPositive && includePlusSign) {
            sign = "+";
        }

        if (this.isNegative) {
            sign = "&minus;";
        }

        var o = this.orderOfMagnitude;
        var os = (o.lt(0)) ? "&times" : "";

        return sign + this.significand.toPrecision(precision) + " &times; 10<sup>" + os + o.abs() + "</sup>";
    }

    toLaTeX(precision = 3, includePlusSign = true) {

    }
}

var application = angular.module("PhysicsParticles", ["ngRoute", "ngSanitize"]);

application.config(function ($routeProvider) {
    $routeProvider
        .when("/", { templateUrl: "table.html", controller: "TableController" })
        .when("/particle/:particleName", { templateUrl: "particle.html", controller: "ParticleController" });
});

application.directive("mathematics", function () {
    return {
        restrict: "E",
        link: function (scope, element, attributes) {
            var contentType = attributes.contentType;
            var content = attributes.content;
            if (typeof (katex) === "undefined") {
                require(["katex"], function (katex) {
                    katex.render(content, element[0]);
                });
            }
            else {
                katex.render(content, element[0]);
            }
        }
    }
});

application.directive("compile", ["$compile", function ($compile) {
    return function (scope, element, attributes) {
        scope.$watch(function (scope) {
            return scope.$eval(attributes.compile);
        }, function (value) {
            element.html(value);
            $compile(element.contents())(scope);
        });
    };
}]);

class Database {
    constructor(data) {
        this._data = data;

        this._particlesObject = {}

        this._data.Particles.forEach(p => {
            this._particlesObject[p.Reference] = p;
        });
    }

    get particles() {
        return this._data.Particles;
    }

    get tableData() {
        return this._particlesObject;
    }

    getParticleWithURLReference(urlReference) {
        var ps = this.particles.filter(p => p.URLReference == urlReference);

        return (ps.length > 0) ? ps[0] : null;
    }
}

application.factory("dataService", ["$http", function ($http) {
    var dataService = {
        data: null,
        getData: function () {
            var that = this;

            if (this.data != null) {
                return new Promise(function (resolve, reject) { return resolve(that.data); });
            }

            return $http.get("particles.json").then(function (response) {
                that.data = response.data;

                return response.data;
            });
        }
    };

    return dataService;
}]);

application.directive("particle", function () {
    return {
        restrict: "E",
        templateUrl: "particle-block.html",
        scope: {
            particle: "=data"
        }
    };
});

function getParticleSymbol(particle) {
    return (!particle) ? "" : "<mathematics content-type=\"latex\" content=\"" + particle.MainSymbol + "\"></mathematics>"
}

application.controller("TableController", ["$scope", "$routeParams", "dataService", "$rootScope", "$location", function TableController($scope, $routeParams, dataService, $rootScope, $location) {

    dataService.getData().then(function (data) {
        var database = new Database(data);

        $scope.particles = database.tableData;
    });

    $scope.getParticleSymbol = getParticleSymbol;

    $scope.getParticleMass = function (particle) {
        if (!particle) { return ""; }

        var mass = particle.Mass.filter(m =>( m.Unit == "eV" || m.Unit == "keV" || m.Unit == "MeV" || m.Unit == "GeV" || m.Unit == "TeV") && m.Rounding == "3sf")[0];

        return mass.HTML;
    }

    $scope.getParticleCharge = function (particle) {
        if (particle.RelativeCharge == "+1") {
            return "+1";
        }
        if (particle.RelativeCharge == "+2/3") {
            return "+2/3";
        }
        if (particle.RelativeCharge == "+1/3") {
            return "+1/3";
        }
        if (particle.RelativeCharge == "0") {
            return "0";
        }
        if (particle.RelativeCharge == "-1/3") {
            return "&minus;1/3";
        }
        if (particle.RelativeCharge == "-2/3") {
            return "&minus;2/3";
        }
        if (particle.RelativeCharge == "-1") {
            return "&minus;1";
        }
    }

    $scope.getChargeHue = function (charge) {
        if (charge == "+1") {
            return 5;
        }
        if (charge == "+2/3") {
            return 15;
        }
        if (charge == "+1/3") {
            return 35;
        }
        if (charge == "0") {
            return 110;
        }
        if (charge == "-1/3") {
            return 170;
        }
        if (charge == "-2/3") {
            return 195;
        }
        if (charge == "-1") {
            return 215;
        }
    }

    $scope.getBackgroundColourForCharge = function (charge) {
        return "hsl(" + $scope.getChargeHue(charge) + ", 100%, 95%)";
    }

    $scope.getBorderColourForCharge = function (charge) {
        return "hsl(" + $scope.getChargeHue(charge) + ", 100%, 85%)";
    }

    $scope.getFontColourForCharge = function (charge) {
        return "hsl(" + $scope.getChargeHue(charge) + ", 70%, 40%)";
    }

    $scope.getColourPropertiesForCharge = function (charge) {
        return "background-color: " + $scope.getBackgroundColourForCharge(charge) + "; border-color: " + $scope.getBorderColourForCharge(charge) + "; color: " + $scope.getFontColourForCharge(charge) + ";";
    }

    $scope.goToParticlePage = function (particle) {
        $location.url("/particle/" + particle.URLReference);
    }
}]);

application.controller("ParticleController", ["$scope", "$routeParams", "dataService", "$rootScope", function ParticleController($scope, $routeParams, dataService, $rootScope) {

    dataService.getData().then(function (data) {
        var database = new Database(data);

        $scope.particle = database.getParticleWithURLReference($routeParams.particleName);
    });

    $scope.getParticleSymbol = getParticleSymbol;

    $scope.getParticleMass = function (particle) {
        if (!particle) { return ""; }

        return  particle.Mass.filter(m =>( m.Unit == "eV" || m.Unit == "keV" || m.Unit == "MeV" || m.Unit == "GeV" || m.Unit == "TeV") && m.Rounding == "3sf")[0].HTML;
    }

    $scope.getParticleRelativeCharge = function (particle) {
        switch (particle.RelativeCharge) {
            case "+1":
                return "+1";
            case "+2/3":
                return "+2/3";
            case "+1/3":
                return "+1/3";
            case "0":
                return "0";
            case "-1/3":
                return "&minus;1/3";
            case "-2/3":
                return "&minus;2/3";
            case "-1":
                return "&minus;1";
        }
    }

    $scope.getParticleCharge = function (particle) {
        if (!particle) { return ""; }

        return  particle.Charge.filter(c => c.Unit == "C" && c.Rounding == "3sf")[0].HTML;
    }

    $scope.getParticleMeanLifetime = function (particle){
        if (!particle){return "";}

        return particle.MeanLifetime.filter(t => t.Rounding == "3sf")[0].HTML;
    }

}]);