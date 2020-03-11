var application = angular.module("PhysicsParticles", ["ngRoute", "ngSanitize"]);

application.config(function ($routeProvider) {
    $routeProvider
        .when("/", { templateUrl: "table.html", controller: "TableController" })
        .when("/list", { templateUrl: "list.html", controller: "ListController" })
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

        var charges = ["+2", "+1", "+2/3", "+1/3", "0", "-1/3", "-2/3", "-1", "-2"];
        var hues = [310, 350, 5, 20, 110, 170, 195, 215, 245];

        this._particlesObject = {}

        this._data.Particles.forEach(p => {
            p.U = {};

            if (p.Mass != undefined && p.Mass == "0") {
                p.U.hasMass = false;
                p.U.mass1 = "0 kg";
                p.U.mass2 = "0 eV";
                p.U.mass3 = "0 u";
            }
            else if (p.Mass != undefined && p.Mass[0] != undefined) {
                p.U.hasMass = (p.Mass[0].Significand == "0") ? false : true;
                p.U.mass1 = p.Mass.filter(m => m.UnitClass == "kg" && m.Rounding == "3sf")[0].HTML;
                p.U.mass2 = p.Mass.filter(m => m.UnitClass == "eV" && m.Rounding == "3sf")[0].HTML;
                p.U.mass3 = p.Mass.filter(m => m.UnitClass == "u" && m.Rounding == "3sf")[0].HTML;
            }

            p.U.relativeCharge = p.RelativeCharge.replace("-", "&minus;");

            if (p.Charge == "0") {
                p.U.charge = "0 C";
            }
            else {
                p.U.charge = p.Charge.filter(c => c.UnitClass == "C" && c.Rounding == "3sf")[0].HTML;
            }

            if (p.MagneticMoment != undefined) {
                p.U.magneticMoment = p.MagneticMoment.filter(mm => mm.Rounding == "none")[0].HTML;
            }

            if (p.MeanLifetime != undefined && p.MeanLifetime != "stable") {
                p.U.meanLifetime = p.MeanLifetime.filter(t => t.UnitClass == "s" && t.Rounding == "3sf")[0].HTML;
            }
            else if (p.MeanLifetime == "stable") {
                p.U.meanLifetime = p.MeanLifetime;
            }

            p.U.generation = ["First", "Second", "Third"][parseInt(p.Generation) - 1];

            var i = charges.indexOf(p.RelativeCharge);

            p.U.hue = hues[i] + Math.random() * 20 - 10;

            if (i == 4) {
                p.U.hue = hues[i] + Math.random() * 80 - 40;
            }

            p.U.style = "background-color: hsl(" + p.U.hue + ", 40%, 50%); background: linear-gradient(140deg, hsl(" + p.U.hue + ", 40%, 55%),  hsl(" + p.U.hue + ", 40%, 45%)); border-color: hsl(" + p.U.hue + ", 40%, 40%); color: hsl(" + p.U.hue + ", 0%, 100%);";

            this._particlesObject[p.Reference] = p;
        });

        console.log(this._particlesObject);
    }

    get particles() {
        return this._data.Particles;
    }

    get gridData() {
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
        database: null,
        getData: function () {
            var that = this;

            if (this.database != null) {
                return new Promise(function (resolve, reject) { return resolve(that.database); });
            }

            return $http.get("particles.json").then(function (response) {
                that.data = response.data;
                that.database = new Database(that.data);

                return that.database;
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

application.controller("TableController", ["$scope", "dataService", "$location", function TableController($scope, dataService, $location) {

    dataService.getData().then(function (database) {
        $scope.particles = database.gridData;
    });

    $scope.getParticleSymbol = getParticleSymbol;

    $scope.goToParticlePage = function (particle) {
        $location.url("/particle/" + particle.URLReference);
    }

}]);

application.controller("ListController", ["$scope", "dataService", "$location", function ListController($scope, dataService, $location) {

    dataService.getData().then(function (database) {
        $scope.particles = database.particles;
    });

    $scope.getParticleSymbol = getParticleSymbol;

    $scope.goToParticlePage = function (particle) {
        $location.url("/particle/" + particle.URLReference);
    }

}]);

application.controller("ParticleController", ["$scope", "$routeParams", "dataService", function ParticleController($scope, $routeParams, dataService) {

    dataService.getData().then(function (database) {
        $scope.particle = database.getParticleWithURLReference($routeParams.particleName);
    });

    $scope.getParticleSymbol = getParticleSymbol;

    $scope.getTagHue = function (c) {
        var n = 0;

        for (var i = 0; i < c.length; i++) {
            n += "abcdefghijklmnopqrstuvwxyz".indexOf(c[i]) * 360 / 26;
        }

        return (n);
    }

}]);